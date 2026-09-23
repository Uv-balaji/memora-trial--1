from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)


# =========================================================
# LOAD COLAB TRAINED ML MODEL
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "ml_model")

kmeans = joblib.load(
    os.path.join(
        MODEL_DIR,
        "kmeans_performance_model.pkl"
    )
)

scaler = joblib.load(
    os.path.join(
        MODEL_DIR,
        "performance_scaler.pkl"
    )
)

ML_FEATURES = joblib.load(
    os.path.join(
        MODEL_DIR,
        "ml_features.pkl"
    )
)

difficulty_mapping = joblib.load(
    os.path.join(
        MODEL_DIR,
        "difficulty_mapping.pkl"
    )
)


print("========================================")
print("MEMORA GENOGAME ML BACKEND")
print("========================================")
print("ML Model: K-Means")
print("Features:", ML_FEATURES)
print("Difficulty Mapping:", difficulty_mapping)
print("========================================")


# =========================================================
# UTILITY
# =========================================================

def safe_number(value, default=0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


# =========================================================
# CREATE ML FEATURES
# =========================================================

def create_ml_features(data):

    # Raw game values
    memory_journey_score = safe_number(
        data.get("memory_journey_score")
    )

    # Enhanced event-derived values. These are optional so the
    # backend remains compatible with older saved sessions.
    memory_accuracy = safe_number(data.get("memory_accuracy"), 0)
    memory_wrong_attempts = safe_number(data.get("memory_wrong_attempts"), 0)
    memory_avg_response_ms = safe_number(data.get("memory_avg_response_ms"), 0)
    matrix_pair_attempts = safe_number(data.get("matrix_pair_attempts"), 0)
    matrix_wrong_pairs = safe_number(data.get("matrix_wrong_pairs"), 0)
    matrix_repeated_cards = safe_number(data.get("matrix_repeated_cards"), 0)
    balloon_touch_accuracy = safe_number(data.get("balloon_touch_accuracy"), 0)
    balloon_wrong_attempts = safe_number(data.get("balloon_wrong_attempts"), 0)
    balloon_reaction_variability = safe_number(data.get("balloon_reaction_variability"), 0)

    memory_matrix_score = safe_number(
        data.get("memory_matrix_score")
    )

    balloon_score = safe_number(
        data.get("balloon_score")
    )

    memory_journey_time = safe_number(
        data.get("memory_journey_time")
    )

    memory_matrix_time = safe_number(
        data.get("memory_matrix_time")
    )

    matrix_moves = safe_number(
        data.get("matrix_moves")
    )

    balloon_max_sequence = safe_number(
        data.get("balloon_max_sequence")
    )


    # -----------------------------------------------------
    # Same feature engineering used during Colab training
    # -----------------------------------------------------

    # Prefer the enhanced event-derived signals when the browser
    # has recorded them; otherwise fall back to the original scores.
    enhanced_memory_score = memory_accuracy if memory_accuracy > 0 else memory_journey_score
    if matrix_pair_attempts > 0:
        enhanced_matrix_score = np.clip(100 - max(0, matrix_pair_attempts - 5) * 4 - matrix_repeated_cards * 0.7, 0, 100)
    else:
        enhanced_matrix_score = memory_matrix_score

    memory_performance = (
        enhanced_memory_score +
        enhanced_matrix_score
    ) / 2


    attention_performance = (
        balloon_touch_accuracy if balloon_touch_accuracy > 0
        else balloon_score
    )


    # Lower response time = better performance. Use per-attempt
    # response time when the enhanced Game 1 instrumentation exists.
    journey_time_for_ml = (
        memory_avg_response_ms * max(1, memory_journey_score > 0)
        if memory_avg_response_ms > 0
        else memory_journey_time
    )
    journey_speed_score = (
        100 -
        (journey_time_for_ml / 5000 * 100)
    )

    journey_speed_score = np.clip(
        journey_speed_score,
        0,
        100
    )


    matrix_speed_score = (
        100 -
        (memory_matrix_time / 90000 * 100)
    )

    matrix_speed_score = np.clip(
        matrix_speed_score,
        0,
        100
    )


    # Fewer pair attempts, wrong pairs and repeated-card selections
    # indicate better repetition/error control.
    moves_for_ml = matrix_pair_attempts if matrix_pair_attempts > 0 else matrix_moves
    matrix_efficiency = (
        100 -
        ((moves_for_ml - 5) / 35 * 100)
        - (matrix_wrong_pairs * 1.5)
        - (matrix_repeated_cards * 0.7)
    )

    matrix_efficiency = np.clip(
        matrix_efficiency,
        0,
        100
    )


    # Higher sequence = better performance
    sequence_performance = (
        balloon_max_sequence / 8 * 100
    )

    sequence_performance = np.clip(
        sequence_performance,
        0,
        100
    )


    return np.array([

        memory_performance,
        attention_performance,
        journey_speed_score,
        matrix_speed_score,
        matrix_efficiency,
        sequence_performance

    ]).reshape(1, -1)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({

        "status": "online",

        "service":
            "Memora presents GenoGame ML Backend",

        "model":
            "K-Means Adaptive Difficulty Engine"

    })


# =========================================================
# ML PREDICTION
# =========================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No JSON data received"

            }), 400


        # -------------------------------------------------
        # Create engineered ML features
        # -------------------------------------------------

        X = create_ml_features(data)


        print("\n========================================")
        print("NEW GAME SESSION")
        print("========================================")

        print("ML input:")
        print(X)


        # -------------------------------------------------
        # Scale using the SAME scaler from Colab
        # -------------------------------------------------

        X_scaled = scaler.transform(X)


        # -------------------------------------------------
        # K-Means prediction
        # -------------------------------------------------

        cluster = int(
            kmeans.predict(X_scaled)[0]
        )


        # -------------------------------------------------
        # Convert cluster → difficulty
        # -------------------------------------------------

        difficulty = difficulty_mapping.get(
            cluster,
            "NORMAL"
        )


        # -------------------------------------------------
        # Calculate distance to each cluster
        # -------------------------------------------------

        distances = kmeans.transform(X_scaled)[0]


        # Convert distances into relative profile scores
        inverse_distances = (
            1 / (distances + 1e-6)
        )

        profile_scores = (
            inverse_distances /
            inverse_distances.sum()
        )


        # -------------------------------------------------
        # Confidence
        #
        # This is NOT medical confidence.
        # It represents how strongly the session
        # matches the selected ML profile.
        # -------------------------------------------------

        confidence = float(
            np.max(profile_scores)
        )


        # -------------------------------------------------
        # Difficulty profile scores
        # -------------------------------------------------

        probabilities = {}

        for cluster_id, score in enumerate(
            profile_scores
        ):

            level = difficulty_mapping.get(
                cluster_id,
                "NORMAL"
            )

            probabilities[level] = round(
                float(score),
                4
            )


        # -------------------------------------------------
        # Recommendation
        # -------------------------------------------------

        if difficulty == "EASY":

            recommendation = (

                "The current game-performance pattern "
                "suggests a supportive difficulty level. "
                "The next activity can use simpler tasks "
                "and gradually increase difficulty as "
                "performance improves."

            )


        elif difficulty == "NORMAL":

            recommendation = (

                "The current game-performance pattern "
                "matches a moderate performance profile. "
                "Continue with the standard difficulty "
                "and compare performance across future "
                "sessions."

            )


        else:

            recommendation = (

                "The current game-performance pattern "
                "supports a more challenging difficulty "
                "level. The next activity can gradually "
                "increase task complexity."

            )


        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        result = {

            "success": True,

            "prediction": difficulty,

            "performance_profile":
                difficulty,

            "cluster":
                cluster,

            "confidence":
                round(
                    confidence,
                    4
                ),

            "probabilities":
                probabilities,

            "recommendation":
                recommendation,

            "model_type":
                "K-Means Adaptive Difficulty Model",

            "ml_features":
                ML_FEATURES,

            "medical_disclaimer": (

                "This system analyzes cognitive-game "
                "performance patterns for adaptive "
                "difficulty and monitoring. It is a "
                "research prototype and must not be "
                "interpreted as a medical diagnosis."

            )

        }


        print("\nML RESULT:")
        print(result)

        print("========================================\n")


        return jsonify(result)


    except Exception as e:

        print(
            "Prediction error:",
            str(e)
        )


        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )