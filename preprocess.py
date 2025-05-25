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


def format_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    for col in ["price", "Longueur", "mileage", "Puissance DIN", "Emission de CO2", "Puissance fiscale"]:
        df[col] = df[col].apply(clean_numstr)

    for col in ["price", "prod_year", "mileage", "Puissance DIN", "Emission de CO2", "Puissance fiscale", "Nombre de places",
                "Nombre de portes"]:
        df[col] = df[col].astype(int)
    df["Longueur"] = df["Longueur"].astype(float)

    df["Mise en circulation"] = pd.to_datetime(df["Mise en circulation"], format="%d/%m/%Y")
    df["circulation_year"] = df["Mise en circulation"].dt.year
    df.drop(columns=["Mise en circulation"], inplace=True)

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


def rare_encode(df: pd.DataFrame, col: str, top_k=5, rare_label="Other"):
    top_categories = df[col].value_counts().nlargest(top_k).index
    df[col] = df[col].apply(lambda x: x if x in top_categories else rare_label)
    df = df.drop(columns=[col])
    return df


def transform_df(df_raw: pd.DataFrame):
    # Drop unwanted cols
    unwanted_cols = ["circulation_year", "Puissance fiscale", "brand", "Provenance"]
    df = df_raw.drop(columns=unwanted_cols)

    # Log transform price
    df["price"] = np.log1p(df["price"])

    # Binary cols
    df["gearbox"] = df["gearbox"].map({"Automatique": 1, "Manuelle": 0})
    df["Première main"] = df["Première main"].map({"Oui": 1, "Non": 0})
    df["Contrôle technique"] = df["Contrôle technique"].map({"Requis": 1, "Non requis": 0})

    df["Norme euro"] = df["Norme euro"].str[-1].astype(int)
    df["Couleur"] = df["Couleur"].str.split().str[0]

    # Rare Encoding
    for col in ["energy", "Couleur"]:
        rare_encode(df, col)

    return df


