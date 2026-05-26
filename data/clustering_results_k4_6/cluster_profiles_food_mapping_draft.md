# Cluster Profiles for Food Recommendation Integration

> Active k=6 food-mapping draft. The recommendation layer should now use the `k=6` model from `data/clustering_results_k4_6/` as the default context signal.

## Status

Adopt `k=6` from now on for the food recommendation prototype.

Why:

1. The k=6 run gives a cleaner split between a broad explorer group, an evening-focused group, a system-heavy low-switching group, and two clearly anomalous tail clusters.
2. The k=6 result is the current active selection in the rerun outputs under `data/clustering_results_k4_6/`.
3. The food layer should prioritize stable, explainable contexts over forcing the earlier k=5 semantic labels.

## Cluster 0: Practical System-Locked Users

Behavioral signals:

- Very low app and category switching
- High system usage
- Low entropy
- Low unique apps and categories
- Low gap between interactions
- Browser/search is relatively elevated compared with other low-engagement signals

Behavioral story:

These users are task-focused and narrow in their activity. The phone is being used as a utility tool rather than a browsing surface. The strongest cue is concentrated, low-switching behavior anchored in system-level or practical actions.

Food direction:

- Vibe: family
- Expected spend: low, mid
- Best fit: dependable, filling, reliable meals

## Cluster 1: Night-Centered Light Users

Behavioral signals:

- Late-night usage lift
- Lower evening and afternoon usage
- Low switching
- Low app/category diversity
- Lower entropy

Behavioral story:

These users show narrow, low-intensity engagement that shifts toward late-night activity. They are not heavy browsers and are more likely to respond to simple, low-friction offers than to discovery-heavy UI.

Food direction:

- Vibe: convenience
- Expected spend: low, mid
- Best fit: late-night snackable, easy-order meals

## Cluster 2: Connected Convenience Seekers

Behavioral signals:

- High app usage and app switching
- High app/category entropy
- High unique apps and categories
- Moderate social behavior
- Slightly lower system dominance

Behavioral story:

These consumers are highly connected and digitally immersed. They move fluidly between apps, consume a constant stream of content, and value speed and convenience in nearly every interaction. Food decisions are influenced by trends, aesthetics, recommendations, and ease of ordering.

Food direction:

- Vibe: convenience
- Expected spend: mid
- Best fit: customizable, shareable, visually appealing meals

## Cluster 3: Balanced Mainstream Consumers

Behavioral signals:

- Moderately strong evening usage
- Slightly lower late-night usage
- Moderate switching
- Moderate diversity and entropy
- No extreme category spikes

Behavioral story:

These consumers represent a broad middle-market audience. They are digitally comfortable, but not highly dependent on novelty. They value familiarity, flexibility, and options that appeal to multiple people or situations.

Food direction:

- Vibe: family, convenience
- Expected spend: mid
- Best fit: practical, consensus-driven meals with broad appeal

## Cluster 4: News Marathon Outliers

Behavioral signals:

- Extreme total duration and session duration
- Strong news engagement
- High afternoon activity
- Low diversity and low switching

Behavioral story:

This is a statistically extreme outlier cluster. It is useful for analysis, but not a stable basis for product strategy.

Food direction:

- Vibe: provisional / not for primary strategy
- Expected spend: provisional
- Best fit: do not anchor the food recommender on this cluster

## Cluster 5: Health-Heavy Anomaly

Behavioral signals:

- Very high health ratio
- Very high late-night usage
- Low switching
- Low diversity
- Strongly atypical pattern relative to the main clusters

Behavioral story:

This is another anomaly cluster. It may be a genuine niche pattern or a data artifact, but it is too small to support a primary recommendation strategy.

Food direction:

- Vibe: provisional / not for primary strategy
- Expected spend: provisional
- Best fit: treat as a fallback-only segment

## What to do next

1. Keep `k=6` as the active cluster model for the food prototype.
2. Add a simple mapping layer from cluster id to food strategy:
	- cluster 0 -> family / reliable
	- cluster 1 -> convenience / late-night
	- cluster 2 -> convenience / visual / trend-friendly
	- cluster 3 -> family / balanced mainstream
	- cluster 4 and 5 -> fallback only
3. Rank dishes from `data/food/food_dish_static_database_with_spend.csv` with `meal_type` first, then `tag`, then `expected_spend`.
4. Keep `expected_spend` as a soft constraint, not a hard filter, unless the requested mode is budget-sensitive.
5. If you want a production-shaped prototype next, build a small inference script that takes today's user-day features, predicts the k=6 cluster, and returns the top 3 dishes with an explanation string.