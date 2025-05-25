import json
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from psycopg2.extensions import connection

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def connect_db() -> connection:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    return conn


def save_data(conn: connection, data: dict):
    url = data.get("url")
    brand = data.get("Marque")
    model = data.get("Titre")
    price = data.get("Prix")
    postcode = data.get("Code Postal")
    production_year = data.get("Année")
    mileage = data.get("Kilométrage")
    gearbox = data.get("Boîte de vitesse")
    energy = data.get("Énergie")

    attrs = {
        k: v for k, v in data.items()
        if k not in ["url", "Marque", "Titre", "Prix", "Code Postal", "Année", "Kilométrage", "Boîte de vitesse", "Énergie"]
    }

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cars (
            url, brand, model, price, postcode, production_year,
            mileage, gearbox, energy, attrs, crawled_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (url) DO NOTHING
    ''', (
        url, brand, model, price, postcode, production_year,
        mileage, gearbox, energy, json.dumps(attrs)
    ))
    conn.commit()


def save_url(conn: connection, url: str, page_num: int):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO urls (url, page_num)
        VALUES (%s, %s)
        ON CONFLICT (url) DO NOTHING
    ''', (url, page_num))
    conn.commit()


def check_url_exist(conn: connection, url: str):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM cars WHERE url = %s LIMIT 1", (url,))
    isExist = cursor.fetchone()
    return isExist


def load_table(table: str):
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    query = f"SELECT * FROM {table};"
    df = pd.read_sql(query, engine)
    return df
