# Cluster Interpretation Draft (KMeans, k=7)

> **Status:** Draft for team review. Generated from `cluster_feature_means.tsv`, `top_features_by_cluster.tsv`, and `clustering_interpretation.txt`. All feature values shown below are **standardized z-scores** (positive = above population average, negative = below). All labels are *behavioral patterns in app usage*, not personality or emotion.

## Headline takeaways

- **Three large clusters cover 92.8% of user-days**: Cluster 0 (40.5%), Cluster 2 (35.5%), Cluster 6 (16.8%).
- **Three "outlier" clusters** (3, 4, 5) together hold only 1.4% of user-days (43 days total). They are statistically distinct but **too small to base recommendation strategy on**.
- **Cluster separation is weak** (silhouette = 0.107). Labels below should be treated as *tendencies*, not hard categories.

## Per-cluster interpretation

### Cluster 0 — "Broad Multi-App Explorers" (n=1176, 40.5%)
**Top distinctive features (z-score vs. population):**
- num_unique_apps **+0.94σ**, num_unique_categories **+0.91σ**
- app_switch_count **+0.87σ**, category_switch_count **+0.87σ**
- app_entropy **+0.82σ**, category_entropy **+0.79σ**
- switch_rate_per_interaction **+0.46σ**
- Slight lift on social and afternoon usage; mild dip on system apps.

**Behavioral story:** These are the high-activity, high-variety days. The user touches many apps across many categories and hops around frequently. Not specialized in any single category — the day is broadly distributed. This is the *modal* behavior in the dataset.

**Caveats:** Total duration is only +0.12σ, so it's not necessarily "long usage" — it's **broad** usage. Could include both an active commuter checking many apps briefly *and* a power-user with a packed schedule.

---

### Cluster 1 — "Single-Task System / Photo Lock-In" (n=168, 5.8%)
**Top distinctive features:**
- system_ratio **+2.51σ**, photo_video_ratio **+0.77σ**, browser_search_ratio **+0.53σ**
- switch_rate_per_interaction **−2.81σ**, avg_gap_between_interactions_log **−2.30σ**
- num_unique_categories **−1.74σ**, num_unique_apps **−1.66σ**
- app_entropy **−1.77σ**, category_entropy **−1.77σ**

**Behavioral story:** Concentrated, narrow usage. The user is locked into one or two apps (heavily skewed toward *system* — settings, launcher, OS-level — plus camera/gallery and browser). Very low switching, very short gaps between interactions = sustained engagement in a single task. May represent setup/configuration sessions, photo organization, or focused browser research.

**Caveats:** "System ratio" being so dominant suggests this might partly capture *device-setup* or *device-troubleshooting* days rather than normal use. Worth checking with raw logs before treating it as a recurring user state.

---

### Cluster 2 — "Daytime Low-Engagement Light Users" (n=1033, 35.5%)
**Top distinctive features:**
- evening_duration_ratio **−0.67σ** (uses phone *less* in the evening than average)
- late_night_duration_ratio **+0.49σ**, morning_duration_ratio **+0.22σ**
- category_switch_count **−0.53σ**, app_switch_count **−0.53σ**
- num_unique_apps **−0.50σ**, num_unique_categories **−0.48σ**
- app/category entropy both **−0.4σ**

**Behavioral story:** Light, narrow daytime usage. They use the phone mostly outside of evening (morning + late-night skew), with few apps, low switching, low entropy. The mirror image of Cluster 6 (which is evening-heavy). Likely captures busy daytime schedules where the phone is used in shorter bursts at the edges of the day.

**Caveats:** "Low-engagement" might be misleading — the better framing is *non-evening-concentrated* light use.

---

### Cluster 3 — "News Marathon Outliers" (n=3, 0.1%) ⚠️ **TOO SMALL**
**Top distinctive features:** avg_session_duration **+26.3σ**, total_duration **+23.8σ**, news_ratio **+7.68σ**, communication_social_ratio **+1.64σ**, afternoon_duration_ratio **+1.63σ**.

**Behavioral story:** Three user-days with extreme session lengths dominated by news consumption.

**Recommendation:** **Drop or merge.** Three observations cannot ground a recommendation strategy. May indicate data-quality issue (one user, multiple very long sessions) or a true rare event.

---

### Cluster 4 — "Late-Night Visual-Social Spikes" (n=13, 0.4%) ⚠️ **TOO SMALL**
**Top distinctive features:** social_visual_ratio **+12.64σ**, late_night_duration_ratio **+0.60σ**, is_weekend **+0.38σ**, category_entropy **+0.47σ**.

**Behavioral story:** Rare days dominated by visual-social apps (Instagram-like, Pinterest-like) in the late-night window, slightly biased toward weekends.

**Recommendation:** Treat as a candidate for *temporal context targeting* (late-night weekend) rather than as a stable cluster.

---

### Cluster 5 — "Gaming Concentration" (n=27, 0.9%) ⚠️ **SMALL**
**Top distinctive features:** games_ratio **+9.83σ**, app_entropy **−1.16σ**, category_entropy **−1.05σ**, app_switch_count **−0.72σ**, avg_gap_between_interactions **+0.56σ**.

**Behavioral story:** Days when the phone is essentially used for one thing — gaming. Low diversity, low switching, longer pauses between interactions (deep gaming sessions). Small but a *clean* behavioral signal.

**Recommendation:** Real pattern but small sample. Treat as a hint for "gaming-mode" context detection rather than a primary cluster.

---

### Cluster 6 — "Evening Wind-Down Users" (n=487, 16.8%)
**Top distinctive features:**
- evening_duration_ratio **+1.64σ** (the strongest evening-concentration signal of any cluster)
- late_night_duration_ratio **−0.78σ** (drops off at night — not night owls)
- morning_duration_ratio **−0.54σ**, afternoon_duration_ratio **−0.52σ**
- app_switch_count **−0.61σ**, category_switch_count **−0.60σ**
- num_unique_apps **−0.58σ**, num_unique_categories **−0.56σ**

**Behavioral story:** A clean, defensible pattern. Usage is heavily concentrated in the evening window, with the phone going relatively quiet by late night. Low app/category diversity, low switching — the user picks up the phone in the evening, does a focused thing, and puts it down. Classic "after-work check-in / wind-down" behavior.

**Caveats:** This is one of the most useful clusters for recommendations because the temporal signal (evening) is strong and the size (n=487) is large enough to act on.

---

## Cluster size summary

| Cluster | Size | % | Useful for strategy? | Suggested label |
|---|---:|---:|---|---|
| 0 | 1176 | 40.5% | Yes | Broad Multi-App Explorers |
| 1 | 168 | 5.8% | Maybe (verify data) | Single-Task System / Photo Lock-In |
| 2 | 1033 | 35.5% | Yes | Daytime Low-Engagement Light Users |
| 3 | 3 | 0.1% | No | News Marathon Outliers |
| 4 | 13 | 0.4% | No | Late-Night Visual-Social Spikes |
| 5 | 27 | 0.9% | Marginal | Gaming Concentration |
| 6 | 487 | 16.8% | Yes (best temporal signal) | Evening Wind-Down |

## Recommendations for the team

1. **The current k=7 model wastes 1.4% of the dataset on three statistical outlier groups.** Consider rerunning at **k=4 or k=5** (which the README already prioritises) — see `data/clustering_results_k4_6/` (option C output) for the comparison.
2. **For the recommendation system, only Clusters 0, 2, and 6 are large enough to anchor a primary strategy.** Cluster 1 can be a secondary state if the team confirms it isn't dominated by device-setup noise.
3. **The strongest actionable signal is temporal**: Cluster 6 (evening-heavy) vs. Cluster 2 (non-evening / edge-of-day) is the cleanest context split in the data.
4. **Don't oversell.** The silhouette score (0.107) explicitly indicates weak/overlapping clusters. Calibrate any team write-up to reflect this.
