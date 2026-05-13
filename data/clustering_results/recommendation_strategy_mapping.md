# Behavioral Cluster → Food Recommendation Strategy Mapping

> **Status:** Draft for team review. Built on top of `cluster_interpretation_draft.md` (KMeans k=7). Each cluster's behavioral pattern is mapped to a concrete recommendation strategy: which dishes/restaurants to surface, when to push them, and what UI signals to use. Strategies for clusters with n < 30 are flagged as **provisional** because of small sample size.

## Design principles

1. **Behavioral context, not personality.** A user can appear in different clusters on different days. The recommendation strategy is keyed off the *current user-day's* cluster, not a permanent label.
2. **Temporal context dominates.** The strongest features separating clusters are temporal (morning/afternoon/evening/late-night) and diversity (switching, entropy). Both should be inputs to the dish-ranking layer.
3. **Default to safe baseline for weak clusters.** When the day-level features sit ambiguously between clusters (low margin), fall back to a population-default ranking instead of forcing a niche strategy.

## Strategy table

| Cluster | Behavioral label | Size | Strategy tier | Primary food strategy |
|---|---|---:|---|---|
| 0 | Broad Multi-App Explorers | 40.5% | **Primary** | **Variety & discovery surface** |
| 1 | Single-Task System / Photo Lock-In | 5.8% | **Secondary** | **Frictionless re-order / one-tap meal** |
| 2 | Daytime Low-Engagement Light Users | 35.5% | **Primary** | **Time-of-day default (breakfast / late-night)** |
| 3 | News Marathon Outliers | 0.1% | Drop | — |
| 4 | Late-Night Visual-Social Spikes | 0.4% | Provisional | Weekend late-night aesthetic restaurants |
| 5 | Gaming Concentration | 0.9% | Provisional | Snackable, no-prep delivery |
| 6 | Evening Wind-Down Users | 16.8% | **Primary** | **Dinner-focused comfort meals** |

---

## Detailed strategies

### Cluster 0 — Broad Multi-App Explorers (Primary)

**Why a strategy works here:** High app/category diversity and switching means the user is in an "open, browsing" mindset that day. They're not locked into one task; they're cognitively available to consider new options.

**Recommendation strategy: Variety & Discovery**
- **Dish ranking:** Boost diversity in the feed. Mix 2–3 cuisines in the top 5 results instead of optimizing for a single best match.
- **Surface:** "Try something new this week" rails, cuisine-spotlight cards, popular-with-people-like-you discovery.
- **Avoid:** Long single-cuisine lists. They'll get bored and bounce.
- **Push notification timing:** Afternoon (slight afternoon-usage lift in this cluster).
- **Risk control:** If user has strong repeat-order history, *do* show that — discovery doesn't mean ignoring stated preferences. Use a 70/30 split (familiar / new).

---

### Cluster 1 — Single-Task System / Photo Lock-In (Secondary)

**Why a strategy works here:** Extreme focus on a single app/task and very low switching = decision-fatigue or in-the-middle-of-something state. Asking them to evaluate options will fail.

**Recommendation strategy: One-Tap Re-Order**
- **Dish ranking:** Top result is **the most likely repeat order** for this user. Skip diversity entirely.
- **Surface:** Persistent "Order your usual" banner; "1-tap reorder" CTA. Skip the menu browse view.
- **Avoid:** Cuisine carousels, "discover new restaurants" — they will not engage with browse-heavy UI.
- **Push notification timing:** Don't push during the cluster's active window; they're locked into something else. Notify *just before* the typical meal time.
- **⚠️ Data caveat:** Cluster is dominated by system_ratio (+2.5σ), which may capture device-setup days. Validate that this cluster also contains users with food-ordering history before treating it as a real "user state" — otherwise it's just noise.

---

### Cluster 2 — Daytime Low-Engagement Light Users (Primary)

**Why a strategy works here:** Light, narrow phone use concentrated in morning and late-night windows (with evening *under-used*). The user opens the phone briefly at the start and end of the day. Decisions need to be quick and the option set small.

**Recommendation strategy: Time-of-Day Default**
- **Morning (their morning-skewed window):** Breakfast, coffee, grab-and-go. Prioritize fast prep, fast delivery, lower decision cost.
- **Late-night:** Comfort snacks, dessert, simple single-serve options (ramen, ice cream, late-night burgers). Avoid family-style multi-dish bundles.
- **Dish ranking:** **Top 3 only.** This user is not going to scroll through 20 options. Show fewer, more decisive choices.
- **Surface:** Quick-pick cards, no carousels, no "explore more."
- **Avoid:** Dinner-time prompts (they're not on the phone then), long menus, decision-heavy promos.
- **Push notification timing:** ~30 minutes before their typical morning window opens; light evening push (often won't see it).

---

### Cluster 3 — News Marathon Outliers (Drop)

**Recommendation strategy:** **None.** With only 3 user-days, any strategy would be overfitting. Drop from primary recommendation logic; fall back to global default.

---

### Cluster 4 — Late-Night Visual-Social Spikes (Provisional)

**Why provisional:** Only 13 user-days, but the signal (social_visual_ratio +12.6σ) is extreme and clean. Worth a small experiment if compute is cheap.

**Provisional strategy: Aesthetic / Shareable Restaurants**
- **Dish ranking:** Boost restaurants with strong visual identity (photo-rich profiles, "Instagrammable" tags), trending dishes.
- **Surface:** Image-forward UI (large photo cards), trending-on-social rail.
- **Timing:** Weekend late-night (cluster has weekend lift + late-night lift).
- **Recommendation:** Run as an A/B experiment on the broader population first; do not build the strategy in for production until validated.

---

### Cluster 5 — Gaming Concentration (Provisional)

**Why provisional:** Only 27 user-days but a clean signal (games_ratio +9.8σ, low switching, long gaps between interactions = deep gaming sessions).

**Provisional strategy: Snack / No-Prep Delivery**
- **Dish ranking:** One-handed, no-utensil food. Finger food, wraps, snacks, energy drinks, pizza slices. De-prioritize dishes that need active eating (noodles, full plates).
- **Surface:** "Gaming fuel" or "Quick snack" rail. Single-tap reorder.
- **Timing:** Match the long-session pattern — push around 2–3 hours into typical gaming windows when hunger is likely.
- **Recommendation:** Build as a content-tag rule (any dish tagged `one-handed = true`) rather than a cluster-specific carousel.

---

### Cluster 6 — Evening Wind-Down Users (Primary)

**Why a strategy works here:** Strongest and cleanest temporal signal in the entire dataset. Evening-concentrated usage, low switching, narrow app set. The user picks up the phone in the evening to do *one focused thing* — and ordering dinner is a natural fit.

**Recommendation strategy: Dinner-Focused Comfort**
- **Dish ranking:** Dinner-time staples, comfort meals, family-style dishes for shared households, single-serve comfort for solo users (verify with order history).
- **Cuisine boost:** Slow-prep, dinner-coded cuisines (Italian, Indian, Chinese family meals, hearty bowls). Down-weight breakfast/cafe items.
- **Surface:** Single hero dinner card → 2–3 secondary options → "Order again" rail. Less browsing-heavy than Cluster 0.
- **Timing:** Push at the *start* of their evening window (since they don't extend into late-night, you have a narrow window — earlier is better than later).
- **Bundling:** Suitable for "meal-for-the-family" bundles, dessert add-ons. Evening = higher willingness to splurge on a complete meal.
- **Avoid:** Late-night snack rails (they're off the phone by then), morning items, very fast/cheap-only ranking (evening users tolerate slower delivery for better meals).

---

## Implementation notes

1. **Cluster assignment at inference time:** The KMeans model + scaler (`scaler.pkl`) is saved. To assign today's user-day to a cluster, you need the same 39-feature vector built from today's app-usage logs, scaled by the saved scaler, then `kmeans.predict(...)`.
2. **Fall-back when cluster confidence is low:** If the user-day's distance to the nearest centroid is far above the cluster's average distance, treat it as "unclustered" and fall back to global recommendations.
3. **Temporal layer:** Even within a cluster, the time-of-day at *request* time should re-weight the recommendation. E.g., a Cluster 6 user opening the app at 10am should not get dinner recommendations; the cluster is a *prior* on behavior, not an override of context.
4. **Avoid recommendation lock-in:** Periodically (e.g., every 7 days) inject a small fraction (~10%) of out-of-cluster recommendations to keep the system exploratory and surface that user-context can shift.

## Open questions for the team

1. Should the recommendation system act on the *user's most common cluster over the last N days* (a personality-like prior), the *current day's cluster* (true context-aware), or a blend? The README suggests context-aware, but stability vs. responsiveness is a real tradeoff.
2. Is the LSApp data joinable to any food-ordering events? If not, this whole layer is currently *unvalidated*; we'd be recommending strategies without observing whether they actually drive orders.
3. Is the silhouette of 0.107 acceptable for a course project deliverable, or should we redo clustering with `k=4–6` (see `clustering_results_k4_6/`) before committing to strategies?
