import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

DATA_PATH = Path("data/diabetes.csv")
MODEL_PATH = Path("models/diabetes_knn.pkl")

ZERO_IS_MISSING = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]

def load_and_preprocess():
    df = pd.read_csv(DATA_PATH)

    df[ZERO_IS_MISSING] = df[ZERO_IS_MISSING].replace(0, np.nan)
    df[ZERO_IS_MISSING] = df[ZERO_IS_MISSING].fillna(df[ZERO_IS_MISSING].mean())

    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    return X, y

def train():
    X, y = load_and_preprocess()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("knn", KNeighborsClassifier(n_neighbors=7)),
        ]
    )

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(y_test, y_pred))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipe,
            "feature_names": list(X.columns),
        },
        MODEL_PATH,
    )
    print(f"Model saved to {MODEL_PATH.absolute()}")

if __name__ == "__main__":
    train()
