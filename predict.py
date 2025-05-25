import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from rare_encoder import RareEncoder

te_cols = ['model', 'postcode']


def load_models():
    rare_encoder = RareEncoder.load("models/rare_encoder.pkl")
    target_encoder = joblib.load('models/target_encoder.pkl')
    preprocessor = joblib.load('models/preprocessor.pkl')
    model = joblib.load('models/random_forest.pkl')
    return rare_encoder, target_encoder, preprocessor, model


def evaluate(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"MAE:  {mae:.3f}")
    print(f"MSE:  {mse:.3f}")
    print(f"R²:   {r2:.3f}")


def predict(X_test: pd.DataFrame) -> pd.DataFrame:
    rare_encoder, target_encoder, preprocessor, model = load_models()

    X_test = rare_encoder.transform(X_test)

    X_te = target_encoder.transform(X_test[te_cols])
    X_test[te_cols] = X_te

    X_test_processed = preprocessor.transform(X_test)

    y_pred = model.predict(X_test_processed)
    y_pred = np.expm1(y_pred).astype(int)

    return y_pred


if __name__ == "__main__":
    data = {
        "model": [
            "renault espace vi phase 2",
            "renault twingo iii phase 2",
            "skoda octavia iv combi phase 2"
        ],
        "price": [38399, 9990, 39479],
        "postcode": ["61", "47", "59"],
        "production_year": [2024, 2022, 2024],
        "mileage": [25660, 30192, 14964],
        "gearbox": [1, 1, 1],
        "energy": [
            "hybride essence électrique",
            "electrique",
            "diesel"
        ],
        "color": ["blanc", "blanc", "bleu"],
        "first_hand": [1, 1, 1],
        "num_places": [7, 4, 5],
        "control_technique": [0, 0, 0],
        "norm_euro": [6, 6, 6],
        "power_DIN": [199, 82, 150],
        "num_doors": [5, 5, 5],
        "length": [4.72, 3.60, 4.70],
        "emission_CO2": [108, 0, 126]
    }

    df_test = pd.DataFrame(data)
    print(df_test)

    X_test = df_test.drop(columns=["price"])
    y_test = df_test["price"]

    y_test_pred = predict(X_test)

    df_result = pd.DataFrame({
        "y_test": y_test,
        "y_test_pred": y_test_pred
    })
    print(df_result)

    evaluate(y_test, y_test_pred)

    # import requests
    #
    # url = "http://127.0.0.1:8000/predict"
    # data = {
    #     "model": "renault espace vi phase 2",
    #     "postcode": "61",
    #     "production_year": 2024,
    #     "mileage": 25660,
    #     "gearbox": 1,
    #     "energy": "hybride essence électrique",
    #     "color": "blanc",
    #     "first_hand": 1,
    #     "num_places": 7,
    #     "control_technique": 0,
    #     "norm_euro": 6,
    #     "power_DIN": 199,
    #     "num_doors": 5,
    #     "length": 4.72,
    #     "emission_CO2": 108
    # }
    #
    # resp = requests.post(url, json=data)
    # print(resp.json())
