from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np

from test import load_models

te_cols = ['model', 'post_code']

rare_encoder, target_encoder, preprocessor, model = load_models()

app = FastAPI()


class CarInput(BaseModel):
    model: str
    post_code: str
    prod_year: int
    mileage: int
    gearbox: int
    energy: str
    color: str
    first_hand: int
    num_places: int
    control_technique: int
    norm_euro: int
    power_DIN: int
    num_doors: int
    length: float
    emission_CO2: int


@app.post("/predict")
def predict_price(car: CarInput):
    input_dict = car.dict()
    df = pd.DataFrame([input_dict])

    df = rare_encoder.transform(df)
    df[te_cols] = target_encoder.transform(df[te_cols])
    df_processed = preprocessor.transform(df)

    y_pred = model.predict(df_processed)
    y_pred = np.expm1(y_pred).astype(int)[0]

    return {"predicted_price": y_pred}


if __name__ == "__main__":
    import requests

    url = "http://127.0.0.1:8000/predict"

    data = {
        "model": "renault espace vi phase 2",
        "post_code": "61",
        "prod_year": 2024,
        "mileage": 25660,
        "gearbox": 1,
        "energy": "hybride essence électrique",
        "color": "blanc",
        "first_hand": 1,
        "num_places": 7,
        "control_technique": 0,
        "norm_euro": 6,
        "power_DIN": 199,
        "num_doors": 5,
        "length": 4.72,
        "emission_CO2": 108
    }

    response = requests.post(url, json=data)
    print(response.json())
