"""Example usage of the food recommendation API."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from food_recommendation_api import (  # type: ignore
    DEFAULT_FEATURES_FILE,
    FoodRecommendationAPI,
    format_user_context,
    format_recommendation,
)


def main() -> None:
    api = FoodRecommendationAPI()

    features_df = pd.read_csv(DEFAULT_FEATURES_FILE, sep="\t")
    print(f"Loaded feature file: {DEFAULT_FEATURES_FILE}")
    print(f"Total rows available: {len(features_df)}")
    print()

    sample_row_index = 0
    sample_row = features_df.iloc[sample_row_index]
    result = api.recommend(
        sample_row,
        meal_type="dinner",
        top_n=3,
    )

    print("Example 1: recommend from a feature row")
    print(f"Example 1 source row_index: {sample_row_index}")
    print(format_user_context(sample_row, api.centroids, result.cluster_id))
    print()
    print(format_recommendation(result))
    print()
    print(f"Follow-up prompt: {result.follow_up_question}")
    print()

    second_row_index = 5
    result_from_file = api.recommend_from_features_file(
        Path(DEFAULT_FEATURES_FILE),
        row_index=second_row_index,
        meal_type=None,
        top_n=5,
    )

    print("Example 2: recommend from the features file")
    print(f"Example 2 source row_index: {second_row_index}")
    print(format_user_context(features_df.iloc[second_row_index], api.centroids, result_from_file.cluster_id))
    print()
    print(format_recommendation(result_from_file))
    print()
    print(f"Follow-up prompt: {result_from_file.follow_up_question}")


if __name__ == "__main__":
    main()