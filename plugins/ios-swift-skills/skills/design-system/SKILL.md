---
name: design-system
description: Build and maintain a SwiftUI design system with semantic tokens (colors, typography, spacing, radius, motion), reusable components, theming, and preview patterns. Use when creating UI components, defining design tokens, setting up theming, or auditing visual consistency.
---

# Design System Skill

> **Attribution**: This skill was created from scratch for this template, drawing on patterns from
> [Microsoft FluentUI Apple](https://github.com/microsoft/fluentui-apple),
> [SwiftUI-Design-System-Pro](https://github.com/muhittincamdali/SwiftUI-Design-System-Pro),
> and [no-problem-dev/swift-design-system](https://github.com/no-problem-dev/claude-code-plugins).
> No code was copied — only architectural principles were referenced.

## Operating Rules

- Always use semantic token names (`Color.primaryAction`), never raw values (`Color(hex: "#007AFF")`)
- Tokens follow a 3-level hierarchy: Primitive → Semantic → Component
- Access tokens via `Environment`, not singletons or static properties
- Every component must support Dark Mode, Dynamic Type, and High Contrast
- Components consume tokens — they never hardcode colors, fonts, or spacing
- Previews are mandatory for every component (see `references/preview-patterns.md`)

## Task Workflow

### Set up a new design system
1. Define primitive tokens (raw color palette, type scale, spacing scale)
2. Map primitives to semantic tokens (see `references/tokens.md`)
3. Create theme infrastructure (see `references/theming.md`)
4. Build foundational components (see `references/components.md`)
5. Add preview patterns for all components

### Add a new component
1. Identify which semantic tokens the component needs
2. Build the component consuming tokens via Environment
3. Create ViewModifier if the component is a styling pattern
4. Add previews: default, dark mode, large text, compact, edge cases
5. Document usage in a code comment

### Audit visual consistency
1. Check all views use semantic tokens (no hardcoded colors/fonts/spacing)
2. Verify Dark Mode support
3. Verify Dynamic Type scaling
4. Check spacing consistency (8pt grid)
5. Verify component reuse vs duplication

### Topic Router

| Topic | Reference |
|-------|-----------|
| Token architecture | `references/tokens.md` |
| Components | `references/components.md` |
| Theming | `references/theming.md` |
| Preview patterns | `references/preview-patterns.md` |

## Design System Checklist

- [ ] No hardcoded colors — all via semantic tokens
- [ ] No hardcoded font sizes — all via typography scale
- [ ] Spacing follows 8pt grid (4, 8, 12, 16, 24, 32, 48)
- [ ] All components support Dark Mode
- [ ] All components support Dynamic Type
- [ ] All components have multi-state previews
- [ ] Components use `Environment` to access tokens
- [ ] Primitive tokens never used directly in views
