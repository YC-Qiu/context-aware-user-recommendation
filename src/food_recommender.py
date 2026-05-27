"""CLI wrapper for the food recommendation API."""

from __future__ import annotations

import argparse
from pathlib import Path

from food_recommendation_api import (  # type: ignore
    DEFAULT_CENTROIDS_FILE,
    DEFAULT_FEATURES_FILE,
    DEFAULT_FOOD_FILE,
    DEFAULT_SCALER_FILE,
    FoodRecommendationAPI,
    format_recommendation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the k=6 food recommendation prototype.")
    parser.add_argument("--features-file", type=Path, default=DEFAULT_FEATURES_FILE)
    parser.add_argument("--food-file", type=Path, default=DEFAULT_FOOD_FILE)
    parser.add_argument("--scaler-file", type=Path, default=DEFAULT_SCALER_FILE)
    parser.add_argument("--centroids-file", type=Path, default=DEFAULT_CENTROIDS_FILE)
    parser.add_argument("--row-index", type=int, default=0, help="Row index from the features file to recommend for.")
    parser.add_argument("--meal-type", type=str, default=None, help="Override meal type: breakfast, lunch, dinner, snack.")
    parser.add_argument("--top-n", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api = FoodRecommendationAPI(
        food_file=args.food_file,
        scaler_file=args.scaler_file,
        centroids_file=args.centroids_file,
    )
    result = api.recommend_from_features_file(
        args.features_file,
        row_index=args.row_index,
        meal_type=args.meal_type,
        top_n=args.top_n,
    )
    print(format_recommendation(result))
    print()
    print(f"Follow-up prompt: {result.follow_up_question}")


if __name__ == "__main__":
    main()