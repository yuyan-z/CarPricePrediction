import re

import numpy as np
import pandas as pd


def drop_nan_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Drop columns that with missing value > 10%
    cols_to_drop = df_raw.columns[df_raw.isna().mean() > 0.1]
    df = df_raw.drop(columns=cols_to_drop)

    # Drop rows with NaN values
    df = df.dropna()

    return df


def clean_numstr(s: str) -> str:
    s = s.replace(",", ".")
    s = re.sub(r"[^\d,.]", "", s)
    return s


def format_num_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    numstr_cols = [
        "price", "Longueur", "mileage", "Puissance DIN", "Emission de CO2",
        "Puissance fiscale"
    ]
    for col in numstr_cols:
        df[col] = df[col].apply(clean_numstr)

    int_cols = [
        "price", "prod_year", "mileage", "Puissance DIN", "Emission de CO2",
        "Puissance fiscale", "Nombre de places", "Nombre de portes"
    ]
    for col in int_cols:
        df[col] = df[col].astype(int)

    df["Longueur"] = df["Longueur"].astype(float)

    return df


def format_str_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    df["post_code"] = np.where(
        df["post_code"] == "",
        "unknown",
        df["post_code"].str[:2]
    )

    cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in cols:
        df[col] = df[col].str.lower()

    return df


def analyze_df(df: pd.DataFrame):
    print("\n-- shape --\n")
    print(df.shape)

    print("\n-- data type --\n")
    print(df.dtypes)

    print("\n-- unique values count --\n")
    print(df.nunique())

    print("\n-- NaN values count --\n")
    print(df.isna().sum())

    print("\n-- description --\n")
    print(df.describe())


def rare_encode(df: pd.DataFrame, col: str, top_k=5, rare_label="Other") -> pd.DataFrame:
    top_categories = df[col].value_counts().nlargest(top_k).index
    df[col] = df[col].apply(lambda x: x if x in top_categories else rare_label)
    df = df.drop(columns=[col])
    return df


def transform_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Log transform price
    df["price"] = np.log1p(df["price"])

    # Binary cols
    df["gearbox"] = df["gearbox"].map({"automatique": 1, "manuelle": 0})
    df["Première main"] = df["Première main"].map({"oui": 1, "non": 0})
    df["Contrôle technique"] = df["Contrôle technique"].map({"requis": 1, "non requis": 0})

    # String cols
    df["Norme euro"] = df["Norme euro"].str[-1].astype(int)
    df["Couleur"] = df["Couleur"].str.split().str[0]

    # Rare Encoding
    for col in ["energy", "Couleur"]:
        rare_encode(df, col)

    return df
