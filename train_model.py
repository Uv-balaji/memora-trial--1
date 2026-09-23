import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib


FEATURES = [
    "memory_journey_score",
    "memory_matrix_score",
    "balloon_score",

    "memory_journey_time",
    "memory_matrix_time",

    "matrix_moves",
    "balloon_max_sequence",

    "hand_detections",
    "face_frames",
    "head_movement"
]


def generate_demo_data(n=2000):

    rng = np.random.default_rng(42)

    rows = []

    for _ in range(n):

        # Three prototype behavioral classes
        label = rng.choice(
            [
                "lower_concern_pattern",
                "monitor_pattern",
                "higher_concern_pattern"
            ],
            p=[0.40, 0.35, 0.25]
        )

        if label == "lower_concern_pattern":

            memory1 = rng.normal(85, 8)
            memory2 = rng.normal(82, 9)
            balloon = rng.normal(82, 10)

            matrix_moves = rng.normal(8, 2)
            balloon_sequence = rng.normal(7, 1)

            memory_time = rng.normal(15000, 3000)
            matrix_time = rng.normal(30000, 5000)

        elif label == "monitor_pattern":

            memory1 = rng.normal(65, 10)
            memory2 = rng.normal(62, 12)
            balloon = rng.normal(60, 12)

            matrix_moves = rng.normal(12, 3)
            balloon_sequence = rng.normal(5, 1.5)

            memory_time = rng.normal(22000, 5000)
            matrix_time = rng.normal(42000, 7000)

        else:

            memory1 = rng.normal(40, 12)
            memory2 = rng.normal(38, 13)
            balloon = rng.normal(35, 14)

            matrix_moves = rng.normal(18, 5)
            balloon_sequence = rng.normal(3, 1.5)

            memory_time = rng.normal(35000, 8000)
            matrix_time = rng.normal(55000, 10000)

        hand = rng.normal(100, 30)
        face = rng.normal(100, 30)
        head = abs(rng.normal(2, 0.8))

        rows.append([
            memory1,
            memory2,
            balloon,

            memory_time,
            matrix_time,

            matrix_moves,
            balloon_sequence,

            hand,
            face,
            head,

            label
        ])

    columns = FEATURES + ["label"]

    df = pd.DataFrame(rows, columns=columns)

    X = df[FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("scaler", StandardScaler()),

        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=8,
                random_state=42,
                class_weight="balanced"
            )
        )
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(
        "Accuracy:",
        accuracy_score(y_test, predictions)
    )

    print(
        classification_report(
            y_test,
            predictions
        )
    )

    joblib.dump(
        {
            "model": model,
            "features": FEATURES
        },
        "model.pkl"
    )

    print("model.pkl created successfully.")


if __name__ == "__main__":
    generate_demo_data()