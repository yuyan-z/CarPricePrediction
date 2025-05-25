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

    numstr_cols = [
        "price", "mileage", "norm_euro", "power_DIN", "length",
        "emission_CO2",
    ]
    for col in numstr_cols:
        df[col] = df[col].apply(clean_numstr)

    int_cols = [
        "price", "production_year", "mileage", "num_places", "norm_euro",
        "power_DIN", "num_doors", "emission_CO2"
    ]
    for col in int_cols:
        df[col] = df[col].astype(int)

    df["length"] = df["length"].astype(float)

    df["postcode"] = np.where(
        df["postcode"] == "",
        "unknown",
        df["postcode"].str[:2]
    )

    df["color"] = df["color"].str.split().str[0]  # Use the first word

    cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in cols:
        df[col] = df[col].str.lower().str.strip()

    # Binary cols
    df["gearbox"] = df["gearbox"].map({"automatique": 1, "manuelle": 0})
    df["first_hand"] = df["first_hand"].map({"oui": 1, "non": 0})
    df["control_technique"] = df["control_technique"].map({"requis": 1, "non requis": 0})

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

