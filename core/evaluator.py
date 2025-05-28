# File: evaluation/core/evaluator.py
import pandas as pd
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from typing import List, Dict, Any
import ast

class CypherEvaluator:
    def __init__(self, test_df: str):
        self.test_df = test_df
        self.metrics = {
            'answer_relevancy': AnswerRelevancyMetric(),
            'correctness': GEval(
                name="Correctness",
                criteria="Determine whether the actual output is factually correct based on the expected output.",
                evaluation_steps=[
                    "Check whether the facts in 'actual output' contradicts any facts in 'expected output'",
                    "You should also heavily penalize omission of detail",
                    "Vague language, or contradicting OPINIONS, are OK"
                ],
                evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            )
        }
    
    def _normalize_cypher(self, query: str) -> str:
        return ' '.join(query.strip().lower().split())
    
    def _compare_results(self, actual: Any, expected: Any) -> bool:
        try:
            if isinstance(actual, str):
                actual = ast.literal_eval(actual)
            if isinstance(expected, str):
                expected = ast.literal_eval(expected)
            return actual == expected
        except:
            return False
    def test_case(self, question, llm_output, expected_output):
        return LLMTestCase(
            input=question,
            actual_output=llm_output,
            expected_output=expected_output
        )
    def _evaluate_single(self, row: pd.Series, llm_cypher: str, llm_answer: Any) -> Dict:
        cypher_test_case = self.test_case(row['question'], llm_cypher, row['cypher'])
        answer_test_case = self.test_case(row['question'], llm_answer, row['expected_output'])
        
        return {
            'question': row['question'],
            'cypher_exact_match': self._normalize_cypher(llm_cypher) == self._normalize_cypher(row['cypher']),
            'cypher_relevancy_score': self.metrics['answer_relevancy'].measure(cypher_test_case),
            'cypher_correctness_score': self.metrics['correctness'].measure(cypher_test_case),
            'execution_accuracy': self._compare_results(llm_answer, row['expected_output']),
            'answer_relevancy_score': self.metrics['answer_relevancy'].measure(answer_test_case),
            'answer_correctness_score': self.metrics['correctness'].measure(answer_test_case),
            'generated_cypher': llm_cypher,
            'generated_answer': llm_answer,
            'expected_cypher': row['cypher'],
            'expected_answer': row['expected_output']
        }
    
    def evaluate(self, bot_results: List[Dict]) -> pd.DataFrame:
        """
        bot_results should be list of dicts with:
        [{
            'question': str,
            'generated_cypher': str,
            'generated_answer': Any
        }]
        """
        results = []
        for br in bot_results:
            row = self.test_df[self.test_df['question'] == br['question']].iloc[0]
            results.append(self._evaluate_single(row, br['generated_cypher'], br['generated_answer']))
        
        return pd.DataFrame(results)
    
    def generate_report(self, df: pd.DataFrame) -> Dict:
        return {
            'avg_cypher_relevancy_score': df['cypher_relevancy_score'].mean(),
            'avg_cypher_correctness_score': df['cypher_correctness_score'].mean(),
            'avg_answer_relevancy_score': df['answer_relevancy_score'].mean(),
            'avg_answer_correctness_score': df['answer_correctness_score'].mean()
        }
