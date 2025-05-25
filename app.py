from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from predict import predict

app = FastAPI()

class CarInput(BaseModel):
    model: str
    postcode: str
    production_year: int
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
    df = pd.DataFrame([car.model_dump()])
    y_pred = predict(df)
    return {"predicted_price": int(y_pred[0])}




