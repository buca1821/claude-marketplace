---
name: app-store
description: App Store optimization and submission — ASO keywords, descriptions, screenshot planning, rejection prevention, and review responses. Use when preparing for App Store launch, optimizing discoverability, or handling reviews and rejections.
---

# App Store Skill

## When to Use

| Task | Reference |
|------|-----------|
| Keyword research and optimization | `references/aso-keywords.md` |
| Writing app description and promotional text | `references/aso-keywords.md` (Description section) |
| Avoiding or handling App Store rejections | `references/rejection-handler.md` |
| Responding to user reviews | `references/review-responses.md` |
| Planning screenshot sequence | See Screenshot Guidelines below |

## Character Limits

| Field | Limit | Notes |
|-------|-------|-------|
| App Name | 30 chars | Highest keyword weight |
| Subtitle | 30 chars | Second highest keyword weight |
| Keyword Field | 100 chars | Comma-separated, no spaces after commas |
| Promotional Text | 170 chars | Not indexed for search, can be updated without review |
| Description | 4000 chars | Not indexed for search on iOS |
| What's New | 4000 chars | Shown prominently on updates |

## Key Principles

### User-Focused Copy
- Lead with benefits, not features
- Speak to user pain points ("Export your workouts in seconds")
- Use clear, simple language
- Include social proof where possible

### Platform Guidelines
- **Never use**: "free", "best", "#1", "most popular"
- **Never mention**: competing platforms (Android, Samsung Health)
- **Never include**: prices in description (they vary by region)
- **Do include**: what makes your app unique

### Search Optimization
- Use high-value keywords naturally
- Don't stuff keywords — Apple penalizes this
- Consider localized search terms for each market
- Update keywords seasonally (e.g., "marathon" before spring)

## Screenshot Guidelines

### Sequence (5-10 screenshots)

1. **Hero shot** — main value proposition (list view with key data)
2. **Core feature** — primary action in progress
3. **Detail view** — item details, charts, stats
4. **Secondary feature** — map, export, sharing, etc.
5. **Multi-format** — additional options, sharing
6. **Social proof or unique feature** — localization, design quality

### Device Frames
- iPhone 6.9" (required): iPhone 16 Pro Max
- iPhone 6.7" (required): iPhone 16 Plus
- iPad 13" (if supporting iPad)

### Tips
- First 3 screenshots appear in search results — make them count
- Use captions that describe benefits, not features
- Localize screenshots for top markets
- Show real data, not lorem ipsum

## Project-Specific Notes

### Data Access Requirements
- App description MUST explain why any sensitive data is needed (e.g., HealthKit, Location, Contacts, etc.)
- Review notes should include test account or detailed steps to test data-dependent features
- Privacy Nutrition Label must accurately reflect all data categories accessed

### Privacy Nutrition Label
Document all data your app accesses:
- List each data category and its purpose (App Functionality, Analytics, etc.)
- Disclose third-party SDK data collection
- Specify whether data is shared with third parties
