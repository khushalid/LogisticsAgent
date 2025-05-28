import pandas as pd
from sklearn.model_selection import train_test_split

class DatasetManager:
    def __init__(self, input_path="data/cypher_eval_with_results.csv"):
        self.input_path = input_path
        self.train_path = "data/train_data.csv"
        self.test_path = "data/test_data.csv"
    
    def split_dataset(self, test_size=0.2):
        """Split dataset and save to train/test files"""
        df = pd.read_csv(self.input_path)
        train_df, test_df = train_test_split(df, test_size=test_size)
        train_df.to_csv(self.train_path, index=False)
        test_df.to_csv(self.test_path, index=False)
        return train_df, test_df
    
    def get_dataset(self):
        """Load pre-split datasets"""
        return (
            pd.read_csv(self.train_path),
            pd.read_csv(self.test_path)
        )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-size", type=float, default=0.3)
    args = parser.parse_args()
    
    dm = DatasetManager()
    dm.split_dataset(test_size=args.test_size)
