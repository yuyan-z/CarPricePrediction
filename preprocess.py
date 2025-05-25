import re

import numpy as np
import pandas as pd


def filter_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Expand attrs
    df_attrs = pd.json_normalize(df_raw["attrs"])
    df = pd.concat([df_raw.drop(columns=["attrs"]), df_attrs], axis=1)

    # Drop unwanted columns
    df.drop(columns=["car_id", "url", "crawled_at", "Crit'Air"], inplace=True)

    # Drop columns that with missing value > 10%
    cols_to_drop = df.columns[df.isna().mean() > 0.1]
    df.drop(columns=cols_to_drop, inplace=True)

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

    df["Couleur"] = df["Couleur"].str.lower()

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


