import pandas as pd
from deepeval.metrics import GEval
from difflib import SequenceMatcher
from chatbot import generate_cypher, execute_cypher
import ast
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv
from deepeval.test_case import LLMTestCaseParams

load_dotenv()

# ---------------------------
# Evaluation Metrics Setup
# ---------------------------
answer_relevancy_metric = AnswerRelevancyMetric()
correctness_metric = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct based on the expected output.",
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradicts any facts in 'expected output'",
        "You should also heavily penalize omission of detail",
        "Vague language, or contradicting OPINIONS, are OK"
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
)

def test_case(input, actual_output, expected_output):
    return LLMTestCase(
        input=input,
        actual_output=actual_output,
        expected_output=expected_output
    )


# ---------------------------
# Enhanced Evaluation Functions
# ---------------------------
def normalize_cypher(query):
    """Normalize Cypher for fair comparison"""
    return ' '.join(query.strip().lower().split())

def compare_execution_results(actual, expected):
    """Compare database execution results"""
    try:
        if isinstance(actual, str):
            actual = ast.literal_eval(actual)
        if isinstance(expected, str):
            expected = ast.literal_eval(expected)
        return actual == expected
    except:
        return False
    

def evaluate_row(row, llm_cypher):
    try:
        user_query = row['question']
        expected_cypher = row['cypher']
        expected_answer = row['expected_output']
        
        # Get LLM response
        llm_answer = execute_cypher(llm_cypher)

        cypher_test_case = test_case(user_query, expected_cypher, llm_cypher)
        answer_test_case = test_case(user_query, expected_answer, llm_answer)
        
        # 1. Cypher Exact Match
        cypher_exact = normalize_cypher(llm_cypher) == normalize_cypher(expected_cypher)
         
        # 2. Cypher Answer Relevancy
        cypher_relevancy_score= answer_relevancy_metric.measure(cypher_test_case)

        # 3. Cypher Correctness Metric
        cypher_correctness_score = correctness_metric.measure(cypher_test_case)
        
        # 4. Answer Accuracy
        execution_match = compare_execution_results(llm_answer, expected_answer)
        
        # 5. Answer Relevancy
        answer_relevancy_score = answer_relevancy_metric.measure(answer_test_case)
        
        # 6. Answer Correctness Metric
        answer_correctness_score = correctness_metric.measure(answer_test_case)
        result = {
            'user_query': user_query,
            'cypher_exact_match': cypher_exact,
            'cypher_relevancy_score': cypher_relevancy_score,
            'cypher_correctness_score': cypher_correctness_score,
            'execution_accuracy': execution_match,
            'answer_relevancy_score': answer_relevancy_score,
            'answer_correctness_score': answer_correctness_score,
            'llm_cypher': llm_cypher,
            'llm_answer': llm_answer
        }
        print(result)
        return result
        
    except Exception as e:
        print(f"Error evaluating query: {user_query} - {str(e)}")
        return {
            'user_query': user_query,
            'error': str(e)
        }

# ---------------------------
# Main Evaluation Workflow
# ---------------------------
if __name__ == "__main__":
    df = pd.read_csv('cypher_eval_with_results.csv')
    results = [evaluate_row(row) for _, row in df.iterrows()]
    print(results)
    eval_df = pd.DataFrame(results)
    eval_df.to_csv("rag_evaluation_results.csv", index=False)
    
    # Generate summary report
    summary = {
        'avg_cypher_relevancy_score': eval_df['cypher_relevancy_score'].mean(),
        'avg_cypher_correctness_score': eval_df['cypher_correctness_score'].mean(),
        'avg_answer_relevancy_score': eval_df['answer_relevancy_score'].mean(),
        'avg_answer_correctness_score': eval_df['answer_correctness_score'].mean(),
    }
    
    print("\n📊 Evaluation Summary:")
    for k, v in summary.items():
        print(f"{k.replace('_', ' ').title()}: {v:.2%}")

    print("✅ Full results saved in evaluation_results.csv")
