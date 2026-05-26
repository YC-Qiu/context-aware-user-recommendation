# Cluster Profiles for Food Recommendation Integration

> Draft cluster documentation for the food recommendation layer. These labels are behavioral summaries meant to sit on top of the existing LSApp clustering pipeline before ranking dishes from `data/food/food_dish_static_database_with_spend.csv`.

## Cluster 0: Connected Convenience Seekers

Behavioral signals:

- High app usage and app switching
- High social/news engagement
- High video and photo behavior
- Moderate entertainment, shopping, and productivity usage

Behavioral story:

These consumers are highly connected and digitally immersed. They move fluidly between apps, consume a constant stream of content, and value speed and convenience in nearly every interaction. Food decisions are influenced by trends, aesthetics, recommendations, and ease of ordering.

Food direction:

- Vibe: convenience
- Expected spend: mid
- Best fit: customizable, shareable, visually appealing meals

## Cluster 1: Practical Home/Family Managers

Behavioral signals:

- Low engagement across most categories
- High browser usage
- Lower social/news activity
- Moderate utilities/productivity
- Lower app switching

Behavioral story:

When these consumers are on their phone, it is because they have a specific purpose. They are practical and task-focused, and not overly reliant on digital stimulation. They value reliability over novelty.

Food direction:

- Vibe: family
- Expected spend: low, mid
- Best fit: dependable, filling, nutritious, family-oriented meals

## Cluster 2: Balanced Mainstream Consumers

Behavioral signals:

- Mostly medium engagement across all categories
- Moderate social, shopping, entertainment, and productivity behavior
- No major highs or lows in usage patterns

Behavioral story:

These consumers represent a broad middle-market audience. They are digitally comfortable, but not highly dependent on technology or driven by novelty. They value familiarity, flexibility, and options that appeal to multiple people or situations.

Food direction:

- Vibe: family, convenience
- Expected spend: mid
- Best fit: practical, consensus-driven meals with broad appeal

## Cluster 3: Mobile-First Entertainment Snackers

Behavioral signals:

- High mobile, games, and entertainment usage
- High app engagement
- Lower browser behavior
- Moderate social engagement

Behavioral story:

These consumers use their phones primarily for entertainment and instant gratification. Their behavior suggests shorter attention spans, frequent engagement sessions, and a preference for quick, frictionless experiences.

Food direction:

- Vibe: convenience
- Expected spend: low
- Best fit: indulgent, snackable, highly craveable options

## Cluster 4: Affluent Experience Seekers

Behavioral signals:

- Higher finance, shopping, and news engagement
- Balanced browser and productivity usage
- Higher evening and late-night activity
- More deliberate and research-oriented behavior

Behavioral story:

These consumers are likely more affluent, intentional, and experience-oriented. They view dining as part of lifestyle and identity expression, and they value quality, craftsmanship, elevated experiences, and curated meals.

Food direction:

- Vibe: comfort
- Expected spend: high
- Best fit: premium, curated, aspirational dining experiences

## Cluster 5: Low-Engagement Routine Users

Behavioral signals:

- Lower app, social, and entertainment engagement
- Higher utility and system usage
- Minimal app switching behavior
- Consistent but low-intensity digital habits

Behavioral story:

These consumers appear highly routine-driven and efficiency-focused. Their digital behavior suggests they use technology primarily as a tool rather than a source of entertainment or discovery. Food choices are likely shaped by habit, affordability, and predictability.

Food direction:

- Vibe: convenience
- Expected spend: low
- Best fit: simple, accessible, predictable everyday meals

## Integration Notes

1. Treat these cluster labels as the semantic layer for the food ranking stage, not as permanent user types.
2. Use `meal_type` from the food CSV to filter by time of day first, then apply cluster-based ranking weights.
3. Use `expected_spend` as a second-pass filter or boost so the final list matches each cluster's spending posture.
4. Cluster 0 and Cluster 2 should favor convenience-forward options with some visual appeal.
5. Cluster 1 and Cluster 5 should favor reliable, routine, low-friction choices.
6. Cluster 3 should surface snackable, fast, low-commitment items.
7. Cluster 4 should surface premium, elevated, higher-intent items.