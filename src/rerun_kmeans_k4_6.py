"""Re-run KMeans clustering for k in {4, 5, 6} and export interpretable artifacts.

This complements `src/clustering_analysis.ipynb`, which auto-picks the k with the
highest silhouette across k=4..8 and lands on k=7. Per the README, the analytical
focus is k in [4, 5, 6]. This script restricts to that range and applies a
balance-aware selection rule (penalize models with microscopic clusters).

Outputs land in `data/clustering_results_k4_6/` so existing artifacts in
`data/clustering_results/` are untouched.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
K_VALUES = [4, 5, 6]
MIN_VIABLE_CLUSTER_FRACTION = 0.02


def load_features(features_file: Path) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    df = pd.read_csv(features_file, sep="\t")
    exclude_cols = {"user_id", "date", "day_of_week", "day_of_week_num"}
    numeric_cols = [
        c
        for c in df.columns
        if df[c].dtype in (np.float64, np.float32, np.int64, np.int32)
        and c not in exclude_cols
    ]
    X = df[numeric_cols].fillna(0).copy()
    return df, X, numeric_cols


def fit_one_k(
    X_scaled: np.ndarray, k: int
) -> tuple[KMeans, np.ndarray, dict[str, float | int]]:
    model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    labels = model.fit_predict(X_scaled)

    sizes = pd.Series(labels).value_counts().sort_index()
    n = len(labels)
    min_frac = float(sizes.min()) / n

    metrics: dict[str, float | int] = {
        "k": k,
        "silhouette_score": float(silhouette_score(X_scaled, labels)),
        "davies_bouldin_score": float(davies_bouldin_score(X_scaled, labels)),
        "calinski_harabasz_score": float(calinski_harabasz_score(X_scaled, labels)),
        "min_cluster_size": int(sizes.min()),
        "max_cluster_size": int(sizes.max()),
        "min_cluster_fraction": min_frac,
        "all_clusters_viable": bool(min_frac >= MIN_VIABLE_CLUSTER_FRACTION),
    }
    return model, labels, metrics


def cluster_feature_means(
    df: pd.DataFrame,
    X_scaled_df: pd.DataFrame,
    labels: np.ndarray,
    feature_cols: list[str],
) -> pd.DataFrame:
    means = X_scaled_df.assign(cluster=labels).groupby("cluster")[feature_cols].mean()
    means.index.name = "cluster"
    return means.reset_index()


def top_features_per_cluster(
    means_df: pd.DataFrame, feature_cols: list[str], top_n: int = 10
) -> pd.DataFrame:
    rows: list[dict] = []
    for _, row in means_df.iterrows():
        cluster = int(row["cluster"])
        feature_vals = row[feature_cols].astype(float)
        ranked = feature_vals.abs().sort_values(ascending=False)
        for rank, feat in enumerate(ranked.head(top_n).index, start=1):
            rows.append(
                {
                    "cluster": cluster,
                    "rank": rank,
                    "feature": feat,
                    "cluster_mean_std": float(feature_vals[feat]),
                    "abs_difference": float(abs(feature_vals[feat])),
                }
            )
    return pd.DataFrame(rows)


def profile_high_med_low(
    means_df: pd.DataFrame, feature_cols: list[str]
) -> pd.DataFrame:
    profile_rows: list[dict] = []
    for _, row in means_df.iterrows():
        cluster = int(row["cluster"])
        record: dict[str, str | int] = {"cluster": cluster}
        for feat in feature_cols:
            val = float(row[feat])
            if val >= 0.5:
                record[feat] = "high"
            elif val <= -0.5:
                record[feat] = "low"
            else:
                record[feat] = "medium"
        profile_rows.append(record)
    return pd.DataFrame(profile_rows)


def _df_to_markdown(df: pd.DataFrame) -> str:
    """Minimal markdown table renderer to avoid the optional `tabulate` dep."""
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                cells.append(f"{v:.4f}")
            else:
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + rows)


def balance_score(metrics: dict[str, float | int]) -> float:
    """Combined score: higher is better.

    Rewards silhouette and viable cluster sizes; penalizes Davies-Bouldin.
    Note this is heuristic; the real choice should also be informed by the
    qualitative cluster interpretation.
    """
    sil = float(metrics["silhouette_score"])
    db = float(metrics["davies_bouldin_score"])
    viable = 1.0 if metrics["all_clusters_viable"] else 0.0
    return sil - 0.05 * db + 0.05 * viable


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    features_file = (
        project_root / "data" / "features" / "lsapp_user_day_clustering_features.tsv"
    )
    out_dir = project_root / "data" / "clustering_results_k4_6"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[load] {features_file}")
    df, X, feature_cols = load_features(features_file)
    print(f"[load] shape={df.shape}, features={len(feature_cols)}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols)
    joblib.dump(scaler, out_dir / "scaler.pkl")

    per_k_metrics: list[dict] = []
    best_models: dict[int, dict] = {}

    for k in K_VALUES:
        print(f"[fit ] k={k} ...")
        model, labels, metrics = fit_one_k(X_scaled, k)
        per_k_metrics.append(metrics)
        best_models[k] = {"model": model, "labels": labels, "metrics": metrics}

        k_dir = out_dir / f"k{k}"
        k_dir.mkdir(exist_ok=True)

        means_df = cluster_feature_means(df, X_scaled_df, labels, feature_cols)
        means_df.to_csv(k_dir / "cluster_feature_means.tsv", sep="\t", index=False)

        top_df = top_features_per_cluster(means_df, feature_cols)
        top_df.to_csv(k_dir / "top_features_by_cluster.tsv", sep="\t", index=False)

        profile_df = profile_high_med_low(means_df, feature_cols)
        profile_df.to_csv(
            k_dir / "cluster_profile_interpretation.tsv", sep="\t", index=False
        )

        df_with = df.copy()
        df_with["cluster"] = labels
        df_with.to_csv(
            k_dir / "lsapp_user_day_features_with_clusters.tsv",
            sep="\t",
            index=False,
        )

        sizes = pd.Series(labels).value_counts().sort_index()
        size_df = pd.DataFrame(
            {
                "cluster": sizes.index,
                "size": sizes.values,
                "fraction": sizes.values / len(labels),
            }
        )
        size_df.to_csv(k_dir / "cluster_sizes.tsv", sep="\t", index=False)

        print(
            f"       sil={metrics['silhouette_score']:.4f} "
            f"db={metrics['davies_bouldin_score']:.4f} "
            f"min={metrics['min_cluster_size']} ({metrics['min_cluster_fraction']*100:.2f}%) "
            f"viable={metrics['all_clusters_viable']}"
        )

    comparison_df = pd.DataFrame(per_k_metrics)
    comparison_df["balance_score"] = comparison_df.apply(
        lambda r: balance_score(r.to_dict()), axis=1
    )
    comparison_df = comparison_df.sort_values(
        "balance_score", ascending=False
    ).reset_index(drop=True)
    comparison_df.to_csv(out_dir / "kmeans_k4_6_comparison.tsv", sep="\t", index=False)

    print()
    print("=== Comparison across k in", K_VALUES, "===")
    print(comparison_df.to_string(index=False))

    chosen_k = int(comparison_df.iloc[0]["k"])
    chosen_metrics = best_models[chosen_k]["metrics"]
    chosen_labels = best_models[chosen_k]["labels"]
    chosen_model = best_models[chosen_k]["model"]

    joblib.dump(chosen_model, out_dir / f"kmeans_chosen_k{chosen_k}.pkl")
    pd.DataFrame({"label": chosen_labels}).to_csv(
        out_dir / f"labels_chosen_k{chosen_k}.tsv", sep="\t", index=False
    )

    summary_lines = [
        "# k=4..6 Rerun Summary",
        "",
        f"Chosen k (by balance score): **{chosen_k}**",
        "",
        "Selection rule combines silhouette (reward), Davies-Bouldin (penalty),",
        "and an indicator for whether all clusters hold >= 2% of the dataset.",
        "",
        "## All candidates",
        "",
        _df_to_markdown(comparison_df),
        "",
        "## Chosen model summary",
        "",
        f"- k = {chosen_k}",
        f"- silhouette = {chosen_metrics['silhouette_score']:.4f}",
        f"- davies-bouldin = {chosen_metrics['davies_bouldin_score']:.4f}",
        f"- calinski-harabasz = {chosen_metrics['calinski_harabasz_score']:.2f}",
        f"- min cluster size = {chosen_metrics['min_cluster_size']} "
        f"({chosen_metrics['min_cluster_fraction']*100:.2f}% of data)",
        f"- max cluster size = {chosen_metrics['max_cluster_size']}",
        f"- all clusters viable (>=2%): {chosen_metrics['all_clusters_viable']}",
        "",
        "## Files",
        "",
        f"- `k{chosen_k}/cluster_feature_means.tsv` - per-cluster means (z-scored)",
        f"- `k{chosen_k}/top_features_by_cluster.tsv` - 10 most distinctive features per cluster",
        f"- `k{chosen_k}/cluster_profile_interpretation.tsv` - high/medium/low profile",
        f"- `k{chosen_k}/lsapp_user_day_features_with_clusters.tsv` - labels joined to features",
        f"- `k{chosen_k}/cluster_sizes.tsv` - cluster size distribution",
        f"- `kmeans_chosen_k{chosen_k}.pkl` - fitted KMeans model",
        f"- `labels_chosen_k{chosen_k}.tsv` - row-aligned cluster labels",
        "- `scaler.pkl` - fitted StandardScaler used for this rerun",
        "- `kmeans_k4_6_comparison.tsv` - full comparison table across k=4,5,6",
    ]
    (out_dir / "SUMMARY.md").write_text("\n".join(summary_lines))

    print()
    print(f"[done] chosen k = {chosen_k}")
    print(f"[done] artifacts in: {out_dir}")


if __name__ == "__main__":
    main()
