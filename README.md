# Context-Aware Food Recommendation Agent (Course Project Prototype)

## Overview
This project studies whether smartphone app-usage behavior can be transformed into stable, interpretable context segments, then used as signals for downstream food recommendation.

Current pipeline focus:
1. Build interaction-level and user-day-level features from LSApp logs.
2. Compare unsupervised clustering methods (KMeans, GMM, Agglomerative).
3. Evaluate candidate models with multiple metrics.
4. Export interpretable cluster profiles and feature summaries.

## Dataset
Primary dataset: LSApp
- Source: https://github.com/aliannejadi/LSApp
- Domain: smartphone app usage logs

Important constraints:
1. LSApp has no emotion labels.
2. This stage does not train supervised emotion models.
3. Clusters are interpreted as behavioral patterns, not psychological diagnoses.

## Repository Structure
- `src/data_prep.ipynb`: raw log cleaning, interaction construction, app-category merge, user-day feature generation.
- `src/clustering_analysis.ipynb`: scaling, PCA, multi-model clustering comparison, interpretation exports.
- `data/features/`: generated feature tables.
- `data/clustering_results/`: model comparison outputs, visualizations, and cluster profiles.

## Reproducible Workflow
1. Install dependencies:
   - `pip install -r requirement.txt`
2. Run notebooks in order:
   - `src/data_prep.ipynb`
   - `src/clustering_analysis.ipynb`
3. Check generated outputs in:
   - `data/features/`
   - `data/clustering_results/`

## Data Outputs

### Interaction-level output
- `data/with_time_diff/lsapp_interactions_with_time_diff_filtered.tsv`

Key notes:
1. One row per `interaction_id`.
2. Filtered with `duration(s) >= 3`.
3. Includes merged `app_category`.
4. Missing category mapping blocks saving (fails fast).

### User-day feature outputs
- `data/features/lsapp_user_day_features.tsv`
- `data/features/lsapp_user_day_clustering_features.tsv`

Typical feature groups:
1. Volume and duration: total usage duration, interaction counts, session counts.
2. Diversity: unique apps/categories, entropy-like behavior indicators.
3. Temporal ratios: morning/afternoon/evening/late-night usage distributions.
4. Switching dynamics: app/category switch counts and rates.
5. Category composition: per-category duration/ratio signals.

## Clustering and Evaluation

Compared methods:
1. KMeans
2. Gaussian Mixture Model (GMM)
3. Agglomerative Clustering

Main metrics:
1. Silhouette Score
2. Davies-Bouldin Score
3. Calinski-Harabasz Score
4. Cluster balance and size distribution

Current analysis constraint in notebook logic:
1. `k` (or `n_components`) starts from 4.
2. Recommendation-focused comparison emphasizes `k = 4, 5, 6`.

Note:
1. `data/clustering_results/` still contains some legacy artifacts from earlier runs (for example files with `k3` in names).
2. Re-running the updated notebook will regenerate outputs under the new `k >= 4` constraint.

## Main Result Artifacts (Current)

Model comparison tables:
- `data/clustering_results/kmeans_comparison.tsv`
- `data/clustering_results/gmm_comparison.tsv`
- `data/clustering_results/agglomerative_comparison.tsv`
- `data/clustering_results/final_clustering_comparison.tsv`
- `data/clustering_results/candidates_comparison_interpretability.tsv`

Visualization outputs:
- `data/clustering_results/pca_scree_plot.png`
- `data/clustering_results/pca_2d_unlabeled.png`
- `data/clustering_results/pca_2d_clusters_KMeans.png`
- `data/clustering_results/kmeans_metrics.png`
- `data/clustering_results/gmm_metrics.png`
- `data/clustering_results/agglomerative_metrics.png`
- `data/clustering_results/interpretability_model_selection.png`

Interpretation and profile outputs:
- `data/clustering_results/cluster_feature_means.tsv`
- `data/clustering_results/cluster_profile_interpretation.tsv`
- `data/clustering_results/top_features_by_cluster.tsv`
- `data/clustering_results/clustering_interpretation.txt`
- `data/clustering_results/lsapp_user_day_features_with_clusters.tsv`
- `data/clustering_results/lsapp_user_day_features_with_clusters_final.tsv`

## Category Mapping Inputs
- `output/UniqueAppNames/unique_app_names.txt`
- `output/UniqueAppNames/app_category_mapping_87.txt`

Merge rules:
1. Exact-match on `app_name`.
2. No heuristic category imputation in code.
3. Any missing category mapping stops output writing.

## Current Status

Completed:
1. Interaction-level preprocessing and filtering pipeline.
2. App-category merge and validation checks.
3. User-day feature extraction and export.
4. Multi-model clustering comparison and metric export.
5. Cluster-level interpretation/profile artifacts.

In progress:
1. Recommendation-focused model finalization under `k >= 4`.
2. Cleanup and regeneration of outputs to remove legacy `k3` artifacts.

Next:
1. Finalize recommendation strategy mapping per behavioral cluster.
2. Connect clusters to dish-level ranking logic.