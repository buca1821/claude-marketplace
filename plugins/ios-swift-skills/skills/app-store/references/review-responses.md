# App Store Review Responses

## When to Respond

| Review Type | Respond? |
|-------------|----------|
| Bug report | ✅ Yes — shows you care |
| Feature request | ✅ Yes — engages power users |
| Negative with actionable feedback | ✅ Yes — opportunity to convert |
| Positive (4-5 stars) | ✅ Brief thank you |
| Trolling / non-constructive | ❌ No |

## Response Templates

**Bug report**: Acknowledge → say if fixed or investigating → offer support email.

**Feature request**: Thank → say if planned or added to backlog.

**Negative**: Empathize → address specific complaint → offer direct support.

**Positive**: Brief thank you, no over-explaining.

## Tone

- Professional, never defensive
- Empathetic — acknowledge frustration before solving
- Concise, specific, action-oriented
- Never ask users to change their rating
- Never copy-paste the same response

## Review Prompts (SKStoreReviewController)

**When**: After positive action, 3+ sessions, not on first launch, not after errors.

**Limits**: Apple caps at 3 prompts per 365-day period. Add a 60-day cooldown.

**Implementation**: Use `SKStoreReviewController.requestReview(in: windowScene)` with session counting and last-prompt tracking via UserDefaults.
