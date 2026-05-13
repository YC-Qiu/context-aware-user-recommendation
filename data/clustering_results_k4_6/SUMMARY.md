# k=4..6 Rerun Summary

Chosen k (by balance score): **5**

Selection rule combines silhouette (reward), Davies-Bouldin (penalty),
and an indicator for whether all clusters hold >= 2% of the dataset.

## All candidates

| k | silhouette_score | davies_bouldin_score | calinski_harabasz_score | min_cluster_size | max_cluster_size | min_cluster_fraction | all_clusters_viable | balance_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.1035 | 2.0782 | 164.6179 | 3 | 1362 | 0.0010 | False | -0.0005 |
| 4 | 0.1027 | 2.1221 | 192.2282 | 3 | 1411 | 0.0010 | False | -0.0034 |
| 6 | 0.0969 | 2.1271 | 155.8086 | 1 | 1136 | 0.0003 | False | -0.0095 |

## Chosen model summary

- k = 5
- silhouette = 0.1035
- davies-bouldin = 2.0782
- calinski-harabasz = 164.62
- min cluster size = 3 (0.10% of data)
- max cluster size = 1362
- all clusters viable (>=2%): False

## Files

- `k5/cluster_feature_means.tsv` - per-cluster means (z-scored)
- `k5/top_features_by_cluster.tsv` - 10 most distinctive features per cluster
- `k5/cluster_profile_interpretation.tsv` - high/medium/low profile
- `k5/lsapp_user_day_features_with_clusters.tsv` - labels joined to features
- `k5/cluster_sizes.tsv` - cluster size distribution
- `kmeans_chosen_k5.pkl` - fitted KMeans model
- `labels_chosen_k5.tsv` - row-aligned cluster labels
- `scaler.pkl` - fitted StandardScaler used for this rerun
- `kmeans_k4_6_comparison.tsv` - full comparison table across k=4,5,6