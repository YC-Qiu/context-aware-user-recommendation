# Food Recommendation Strategy Mapping — k=5 Variant

> Companion to `INTERPRETATION_k5.md`. This is the rerun-cluster version of `data/clustering_results/recommendation_strategy_mapping.md`. Use this if the team adopts k=5 as the final model.

## Strategy table

| Cluster | Behavioral label | Size | Tier | Primary strategy |
|---|---|---:|---|---|
| 0 | Broad Multi-App Explorers | 43.0% | **Primary** | Variety & Discovery |
| 1 | Single-Task System / Photo Lock-In | 6.7% | **Secondary** | One-Tap Re-Order |
| 2 | Narrow Light Usage (no temporal signal) | 46.9% | **Primary** | Time-of-Day Default at *request time* |
| 3 | Social-News & Productivity Heavy | 3.3% | **Experimental** | Focused / Low-Friction Picks |
| 4 | News Marathon Outliers | 0.1% | Drop | — |

## Strategy detail (changes vs. k=7 mapping)

### Cluster 0 — Broad Multi-App Explorers
Unchanged from `recommendation_strategy_mapping.md` (same behavioral pattern at k=7 and k=5). **Variety & Discovery**: diverse cuisines in top results, exploration rails, 70/30 familiar/new split.

### Cluster 1 — Single-Task System / Photo Lock-In
Unchanged from k=7 mapping. **One-Tap Re-Order**: top result is the user's most likely repeat; skip browse UI; push just before typical meal time. ⚠ Validate cluster isn't device-setup noise.

### Cluster 2 — Narrow Light Usage (MERGED) — strategy now relies more on request-time context

The k=5 model merges k=7's "Daytime Light" and "Evening Wind-Down" clusters into one big bucket. **Cluster membership alone doesn't tell you when to push dinner content.** So the strategy splits at runtime by *current* time-of-day:

| Time of request | Strategy for Cluster 2 users |
|---|---|
| Morning (6–10am) | Breakfast / grab-and-go / fast prep. Top 3 only, no browse. |
| Daytime (10am–5pm) | Light defaults; user is unlikely to engage deeply — don't push hard. |
| **Evening (5–9pm)** | **Dinner-focused comfort meals, family-style options, dessert add-ons.** This is the lost-at-cluster-level dinner signal — recover it from request time. |
| Late night (9pm–3am) | Comfort snacks, single-serve, simple. |

In other words: at k=5, the recommendation system **must** use temporal features from the current request, not just the cluster ID, to do dinner targeting well. Build the time-of-day re-weighting layer first; cluster ID is the secondary input.

### Cluster 3 — Social-News & Productivity Heavy (NEW)

**Strategy: Focused / Low-Friction Picks**
- **Dish ranking:** Reliable, decisive options. The user is in an information-consumption / work mode and won't tolerate menu-browsing decision fatigue. Top 3 results, no scroll-to-explore.
- **Cuisine bias:** Slight tilt to lunch staples and "desk meals" if request is during work hours; comfort meals if evening (cluster has mild evening lift).
- **Surface:** "Quick pick for a focused day" card. No carousel-of-25-restaurants UI.
- **Avoid:** Promotional flooding, discovery rails, novelty cuisines.
- **Push timing:** Light. This user has the phone open already; *in-app* surfacing matters more than push notifications.
- **A/B test:** Compare against the default Cluster 0 strategy to see if narrowing the choice set actually lifts conversion for this segment.

### Cluster 4 — News Marathon Outliers
Drop. n=3 cannot ground any strategy.

## Implementation deltas vs. the k=7 version

If you migrate from the k=7 strategy to the k=5 strategy:

1. **Re-introduce a request-time temporal layer.** Under k=7, Cluster 6 (evening) gave you dinner targeting *for free* from cluster membership. Under k=5, you have to apply time-of-day weights yourself on top of Cluster 2. **This is a strict requirement, not optional.**
2. **Add a new strategy bucket** for Cluster 3 (Social-News/Productivity). The recommendation engine needs to recognize this cluster ID and route to the "Focused / Low-Friction" picker.
3. **Drop strategies for k=7's tiny clusters** (Late-Night Visual-Social spikes, Gaming Concentration). They no longer exist as distinct groups under k=5 — they got absorbed into Clusters 0, 2, or 3. If you still want gaming/late-night-aesthetic targeting, do it via **content tags + request-time features**, not via cluster membership.
4. **Persist the outlier handling.** Cluster 4 still exists at k=5 (same 3 user-days as k=7's cluster 3). The drop-and-fallback logic carries over unchanged.

## Open questions for the team

Same as the k=7 version, plus:

5. **Does losing the explicit evening cluster bother us?** If dinner-time targeting is the #1 use case of this system, k=7 keeps it as a structural feature. If we trust the temporal-layer-on-top approach (recommended), k=5 is cleaner.
6. **Do we want to refit Cluster 3 with more careful interpretation?** "Social-News + Productivity heavy" is a tentative label based on top features; we should look at actual app names in this cluster's user-days before committing to a strategy.
