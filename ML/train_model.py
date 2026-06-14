"""
Train the Decision Tree logic-classifier and save to logic_classifier.pkl.

Run:
    python ML/train_model.py
"""
import os
import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "dataset.csv")
OUT = os.path.join(HERE, "logic_classifier.pkl")

FEATURES = ["num_conditions", "num_loops", "num_functions",
            "num_operators", "code_length", "complexity_score"]


def main():
    df = pd.read_csv(DATA)
    X = df[FEATURES].values
    labels = sorted(df["label"].unique().tolist())
    y = df["label"].map({l: i for i, l in enumerate(labels)}).values

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model = DecisionTreeClassifier(max_depth=6, random_state=42)
    model.fit(X_tr, y_tr)

    pred = model.predict(X_te)
    print(f"Accuracy: {accuracy_score(y_te, pred):.3f}")
    print(classification_report(y_te, pred, target_names=labels, zero_division=0))

    joblib.dump({"model": model, "labels": labels, "features": FEATURES}, OUT)
    print(f"Saved model -> {OUT}")


if __name__ == "__main__":
    main()
