# k=5 Cluster Interpretation (Rerun output)

> **Status:** Draft for team review. The rerun script (`src/rerun_kmeans_k4_6.py`) restricted KMeans to k in {4, 5, 6} per the README, then picked the best k by a balance-aware score (silhouette − 0.05·DB + 0.05·viability). **k=5 was selected.** All feature values below are standardized z-scores.

## TL;DR — what changed vs. the original k=7 result

| Aspect | k=7 (original) | k=5 (rerun) |
|---|---|---|
| Silhouette | 0.107 | 0.103 (≈ tied) |
| Davies-Bouldin | 2.04 | 2.08 |
| Number of tiny (<2%) clusters | 3 (n=3, 13, 27) | 1 (n=3) |
| Notable cluster gained | — | "Social-News & Productivity" (n=96, 3.3%) |
| Notable cluster lost | — | **Explicit "Evening Wind-Down"** split (merged into narrow-usage) |
| Outlier news cluster | n=3 | n=3 (persistent — these 3 user-days are real outliers regardless of k) |

**Headline tradeoff:** k=5 is more balanced and surfaces a new behavioral pattern (Social-News / Productivity heavy days), but **loses the explicit evening-vs-non-evening split** that was the most actionable temporal signal in k=7.

## Per-cluster interpretation (k=5)

### Cluster 0 — "Broad Multi-App Explorers" (n=1251, 43.0%)
Same pattern as k=7 cluster 0. High diversity, high switching, exploratory days.
- num_unique_apps **+0.89σ**, num_unique_categories **+0.86σ**, app_switch_count **+0.77σ**, app_entropy **+0.80σ**.

### Cluster 1 — "Single-Task System / Photo Lock-In" (n=195, 6.7%)
Same as k=7 cluster 1. Concentrated narrow usage, system/photo/browser-heavy, very low switching.
- system_ratio **+2.19σ**, switch_rate_per_interaction **−2.69σ**, num_unique_apps **−1.65σ**.

### Cluster 2 — "Narrow Light Usage" (n=1362, 46.9%) — **MERGED CLUSTER**
This cluster is the **merge of k=7's clusters 2 and 6** (Daytime Low-Engagement + Evening Wind-Down). At k=5, KMeans no longer splits these two patterns.
- num_unique_apps **−0.58σ**, app/category_switch **−0.58σ**, app/category_entropy **−0.49/−0.47σ**.
- Temporal features (morning/afternoon/evening/late-night) are all near zero — no time-of-day signal.

**Implication for recommendations:** Without the evening split, you can't use cluster membership alone to surface dinner content. You must inject the time-of-day at *request time* on top of the cluster. (This was already the recommended design in `recommendation_strategy_mapping.md`, but k=7 used to give it as a free bonus.)

### Cluster 3 — "Social-News & Productivity Heavy" (n=96, 3.3%) — **NEW PATTERN**
A new cluster that wasn't separable at k=7.
- social_news_ratio **+4.59σ** (Reddit-like / news-discussion apps)
- productivity_ratio **+1.40σ**
- Mild evening lift **+0.29σ**, low communication overall (−0.4 to −0.5σ across communication categories).

**Behavioral story:** Days when users heavily engage with news-aggregator/forum apps *and* productivity apps, while social/messaging is suppressed. Could capture: catching-up-on-news during work breaks, deep-reading days, or "informed loner" sessions. Decent size (n=96) — actionable.

**Recommendation hook:** Information-seeking, focused mood. Surface dishes that don't require complex choice (less browsing tolerance). Push slightly later in the day. Worth A/B testing.

### Cluster 4 — "News Marathon Outliers" (n=3, 0.1%) — **OUTLIER, PERSISTS**
The same 3 user-days that formed k=7's cluster 3. They are extreme outliers (avg_session_duration **+26σ**) and survive every choice of k from 4 to 8. Almost certainly noise or a single data anomaly. Drop from primary recommendation logic.

## Cluster size distribution (k=5)

| Cluster | Size | % | Useful? |
|---|---:|---:|---|
| 0 | 1251 | 43.0% | ✓ Primary |
| 1 | 195 | 6.7% | ✓ Secondary |
| 2 | 1362 | 46.9% | ✓ Primary (but no temporal signal) |
| 3 | 96 | 3.3% | ✓ Marginal but actionable |
| 4 | 3 | 0.1% | ✗ Drop |

## Which k should you actually ship?

This is a team call. Honest assessment:

**Pick k=5 if** you value:
- Balanced cluster sizes
- Discovering a new pattern (Social-News/Productivity)
- Matching the README's stated focus (k=4–6)
- A simpler 4-strategy recommendation system (after dropping the outlier cluster)

**Pick k=7 (original) if** you value:
- Having an explicit "Evening Wind-Down" cluster to drive dinner recommendations directly from cluster membership
- The strongest temporal signal in the data being preserved at the cluster level

**Pick k=4 if** you want maximum simplicity (only 2 large clusters + 1 small + 1 outlier), but you'll lose all the secondary patterns. Probably not worth it.

**My recommendation: k=5, with time-of-day always applied as a separate signal on top.** This matches the README focus, is the most defensible academically (better cluster balance), and the lost "evening" signal can be reconstructed from raw request-time features anyway.

## What was NOT redone

The rerun only refit KMeans. **GMM and Agglomerative were not redone** with the new scoring; the original notebook can be re-run if the team wants a full method-vs-k comparison. Given the silhouette scores from the original run (GMM and Agglomerative were both worse than KMeans), this is unlikely to change the answer, but it's a loose end.
