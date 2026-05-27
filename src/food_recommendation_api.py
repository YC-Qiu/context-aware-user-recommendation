"""Reusable API for the context-aware food recommendation prototype."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FEATURES_FILE = PROJECT_ROOT / "data" / "features" / "lsapp_user_day_clustering_features.tsv"
DEFAULT_FOOD_FILE = PROJECT_ROOT / "data" / "food" / "food_dish_static_database_with_spend.csv"
DEFAULT_SCALER_FILE = PROJECT_ROOT / "data" / "clustering_results_k4_6" / "scaler.pkl"
DEFAULT_CENTROIDS_FILE = PROJECT_ROOT / "data" / "clustering_results_k4_6" / "k6" / "cluster_feature_means.tsv"

TIME_TO_MEAL = {
    "breakfast": (5, 10),
    "lunch": (10, 15),
    "dinner": (15, 21),
    "snack": (21, 24),
}

SPEND_SCORE = {"low": 3, "mid": 2, "high": 1}
SPEND_ORDER = {"low": 0, "mid": 1, "high": 2}

CLUSTER_STRATEGIES = {
    0: {
        "label": "Practical System-Locked Users",
        "vibe": "family",
        "spend": ["low", "mid"],
        "tag_priority": ["family", "comfort", "convenience"],
        "meal_priority": ["dinner", "lunch", "snack", "breakfast"],
        "description": "Reliable, filling, low-friction meals.",
    },
    1: {
        "label": "Night-Centered Light Users",
        "vibe": "convenience",
        "spend": ["low", "mid"],
        "tag_priority": ["convenience", "comfort", "family"],
        "meal_priority": ["snack", "dinner", "lunch", "breakfast"],
        "description": "Late-night, easy-order food with minimal browsing cost.",
    },
    2: {
        "label": "Connected Convenience Seekers",
        "vibe": "convenience",
        "spend": ["mid", "low", "high"],
        "tag_priority": ["convenience", "family", "comfort"],
        "meal_priority": ["lunch", "dinner", "breakfast", "snack"],
        "description": "Visual, shareable, customizable meals that feel current.",
    },
    3: {
        "label": "Balanced Mainstream Consumers",
        "vibe": "family",
        "spend": ["mid", "low", "high"],
        "tag_priority": ["family", "convenience", "comfort"],
        "meal_priority": ["dinner", "lunch", "breakfast", "snack"],
        "description": "Broad-appeal meals that work for multiple people or occasions.",
    },
    4: {
        "label": "News Marathon Outliers",
        "vibe": "fallback",
        "spend": ["mid", "low", "high"],
        "tag_priority": ["comfort", "convenience", "family"],
        "meal_priority": ["lunch", "dinner", "snack", "breakfast"],
        "description": "Fallback-only bucket; do not anchor the recommender here.",
    },
    5: {
        "label": "Health-Heavy Anomaly",
        "vibe": "fallback",
        "spend": ["low", "mid", "high"],
        "tag_priority": ["convenience", "comfort", "family"],
        "meal_priority": ["breakfast", "lunch", "dinner", "snack"],
        "description": "Fallback-only bucket; treat as anomalous until validated.",
    },
}


@dataclass(frozen=True)
class RecommendationResult:
    cluster_id: int
    cluster_label: str
    dishes: pd.DataFrame
    follow_up_question: str


def format_user_context(user_features: pd.Series, centroids: pd.DataFrame, cluster_id: int, top_n: int = 6) -> str:
    feature_columns = centroids.columns.tolist()
    feature_frame = _align_features(user_features, feature_columns)
    centroid_row = centroids.loc[cluster_id]
    absolute_deltas = (feature_frame.iloc[0] - centroid_row).abs().sort_values(ascending=False)

    metadata_lines = [
        "user_context:",
        f"  user_id: {user_features.get('user_id', 'unknown')}",
        f"  date: {user_features.get('date', 'unknown')}",
        f"  day_of_week_num: {user_features.get('day_of_week_num', 'unknown')}",
        f"  is_weekend: {user_features.get('is_weekend', 'unknown')}",
        f"  assigned_cluster: {cluster_id}",
    ]

    signal_rows = []
    for feature_name in absolute_deltas.head(top_n).index:
        signal_rows.append(
            {
                "feature": feature_name,
                "user_value": float(feature_frame.iloc[0][feature_name]),
                "cluster_mean": float(centroid_row[feature_name]),
                "abs_delta": float(absolute_deltas[feature_name]),
            }
        )

    signal_df = pd.DataFrame(signal_rows)
    return "\n".join(metadata_lines + ["", signal_df.to_string(index=False)])


def load_food_catalog(food_file: Path) -> pd.DataFrame:
    food_df = pd.read_csv(food_file)
    required_columns = {"dish", "tag", "meal_type", "expected_spend"}
    missing = required_columns.difference(food_df.columns)
    if missing:
        raise ValueError(f"Food catalog is missing columns: {sorted(missing)}")
    return food_df.copy()


def load_centroids(centroids_file: Path) -> pd.DataFrame:
    centroids = pd.read_csv(centroids_file, sep="\t")
    if "cluster" not in centroids.columns:
        raise ValueError("Centroid table must include a 'cluster' column.")
    return centroids.set_index("cluster")


def load_scaler(scaler_file: Path):
    return joblib.load(scaler_file)


def infer_meal_type(requested_meal_type: str | None, current_time: datetime | None) -> str:
    if requested_meal_type:
        meal_type = requested_meal_type.strip().lower()
        if meal_type not in {"breakfast", "lunch", "dinner", "snack"}:
            raise ValueError("meal_type must be one of breakfast, lunch, dinner, snack")
        return meal_type

    hour = (current_time or datetime.now()).hour
    for meal_type, (start_hour, end_hour) in TIME_TO_MEAL.items():
        if start_hour <= hour < end_hour:
            return meal_type
    return "snack"


def _align_features(row: pd.Series, feature_columns: Iterable[str]) -> pd.DataFrame:
    data = {column: float(row.get(column, 0.0)) for column in feature_columns}
    return pd.DataFrame([data], columns=list(feature_columns))


def predict_cluster(user_features: pd.Series, scaler, centroids: pd.DataFrame) -> tuple[int, float]:
    feature_columns = centroids.columns.tolist()
    feature_frame = _align_features(user_features, feature_columns)
    scaled_values = scaler.transform(feature_frame)

    centroid_matrix = centroids.to_numpy(dtype=float)
    distances = np.linalg.norm(centroid_matrix - scaled_values, axis=1)
    cluster_index = int(np.argmin(distances))
    cluster_id = int(centroids.index[cluster_index])
    return cluster_id, float(distances[cluster_index])


def score_foods(food_df: pd.DataFrame, cluster_id: int, meal_type: str) -> pd.DataFrame:
    strategy = CLUSTER_STRATEGIES.get(cluster_id, CLUSTER_STRATEGIES[3])
    candidate_df = food_df.copy()

    candidate_df["meal_match"] = (candidate_df["meal_type"].str.lower() == meal_type).astype(int)
    candidate_df["tag_rank"] = candidate_df["tag"].str.lower().map(
        lambda tag: strategy["tag_priority"].index(tag) if tag in strategy["tag_priority"] else len(strategy["tag_priority"])
    )
    candidate_df["meal_rank"] = candidate_df["meal_type"].str.lower().map(
        lambda meal: strategy["meal_priority"].index(meal) if meal in strategy["meal_priority"] else len(strategy["meal_priority"])
    )
    candidate_df["spend_rank"] = candidate_df["expected_spend"].str.lower().map(
        lambda spend: SPEND_ORDER.get(spend, len(SPEND_ORDER))
    )
    candidate_df["spend_weight"] = candidate_df["expected_spend"].str.lower().map(
        lambda spend: SPEND_SCORE.get(spend, 0)
    )

    candidate_df["strategy_score"] = (
        candidate_df["meal_match"] * 10
        + (len(strategy["tag_priority"]) - candidate_df["tag_rank"])
        + (len(strategy["meal_priority"]) - candidate_df["meal_rank"])
        + candidate_df["spend_weight"]
    )

    return candidate_df.sort_values(
        by=["strategy_score", "meal_match", "tag_rank", "meal_rank", "spend_rank", "dish"],
        ascending=[False, False, True, True, True, True],
    ).reset_index(drop=True)


def build_follow_up_question(cluster_id: int, meal_type: str) -> str:
    strategy = CLUSTER_STRATEGIES.get(cluster_id, CLUSTER_STRATEGIES[3])

    if cluster_id == 1:
        return "Do you feel like trying something else, or should I keep it simple with more easy-order options?"

    if cluster_id == 2:
        return (
            f"Do you want me to lean more toward {strategy['vibe']} options, "
            "or should I shift the next set toward a different cuisine?"
        )

    if cluster_id == 3:
        return (
            f"Do you want more family-style picks for {meal_type}, "
            "or should I narrow the next round to quick convenience food?"
        )

    if cluster_id in {4, 5}:
        return "Do you feel like trying something else, or should I fall back to safer everyday options?"

    return f"Do you feel like trying something else, or should I stay with more {strategy['vibe']} options?"


class FoodRecommendationAPI:
    """Small in-process API for the food recommendation prototype."""

    def __init__(
        self,
        *,
        food_file: Path = DEFAULT_FOOD_FILE,
        scaler_file: Path = DEFAULT_SCALER_FILE,
        centroids_file: Path = DEFAULT_CENTROIDS_FILE,
    ) -> None:
        self.food_df = load_food_catalog(food_file)
        self.scaler = load_scaler(scaler_file)
        self.centroids = load_centroids(centroids_file)

    def recommend(
        self,
        user_features: pd.Series,
        *,
        meal_type: str | None = None,
        top_n: int = 3,
        current_time: datetime | None = None,
    ) -> RecommendationResult:
        cluster_id, distance = predict_cluster(user_features, self.scaler, self.centroids)
        strategy = CLUSTER_STRATEGIES.get(cluster_id, CLUSTER_STRATEGIES[3])
        resolved_meal_type = infer_meal_type(meal_type, current_time)
        ranked_foods = score_foods(self.food_df, cluster_id, resolved_meal_type)
        follow_up_question = build_follow_up_question(cluster_id, resolved_meal_type)

        top_foods = ranked_foods.head(top_n).copy()
        top_foods.insert(0, "cluster_id", cluster_id)
        top_foods.insert(1, "cluster_label", strategy["label"])
        top_foods.insert(2, "cluster_distance", distance)
        top_foods.insert(3, "recommended_meal_type", resolved_meal_type)
        top_foods.insert(4, "strategy_vibe", strategy["vibe"])
        top_foods.insert(5, "strategy_description", strategy["description"])

        return RecommendationResult(
            cluster_id=cluster_id,
            cluster_label=strategy["label"],
            dishes=top_foods,
            follow_up_question=follow_up_question,
        )

    def recommend_from_features_file(
        self,
        features_file: Path = DEFAULT_FEATURES_FILE,
        *,
        row_index: int = 0,
        meal_type: str | None = None,
        top_n: int = 3,
        current_time: datetime | None = None,
    ) -> RecommendationResult:
        features_df = pd.read_csv(features_file, sep="\t")
        if row_index < 0 or row_index >= len(features_df):
            raise IndexError(f"row-index must be between 0 and {len(features_df) - 1}")
        return self.recommend(
            features_df.iloc[row_index],
            meal_type=meal_type,
            top_n=top_n,
            current_time=current_time,
        )


def format_recommendation(result: RecommendationResult) -> str:
    display_columns = [
        "dish",
        "tag",
        "meal_type",
        "expected_spend",
        "cluster_id",
        "cluster_label",
        "strategy_vibe",
        "strategy_score",
    ]
    lines = [f"cluster_id: {result.cluster_id}", f"cluster_label: {result.cluster_label}", ""]
    lines.append(result.dishes[display_columns].to_string(index=False))
    lines.extend(["", f"follow_up_question: {result.follow_up_question}"])
    return "\n".join(lines)
