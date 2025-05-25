import pandas as pd
import joblib


class RareEncoder:
    def __init__(self, top_k: int = 5, rare_label: str = "other"):
        self.top_k = top_k
        self.rare_label = rare_label
        self.top_categories_dict = {}

    def fit(self, df: pd.DataFrame, cols: list[str]):
        for col in cols:
            top_categories = df[col].value_counts().nlargest(self.top_k).index
            self.top_categories_dict[col] = set(top_categories)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        for col, top_categories in self.top_categories_dict.items():
            df_copy[col] = df_copy[col].apply(lambda x: x if x in top_categories else self.rare_label)
        return df_copy

    def fit_transform(self, df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        self.fit(df, cols)
        return self.transform(df)

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        return joblib.load(path)
