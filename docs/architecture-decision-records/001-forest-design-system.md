# ADR-001: Adoption of Forest Design System

## Status: Accepted
## Date: 2026-04-05

## Context
The project originally used Bootstrap 5 + Tailwind v3 with a custom dark theme. We needed a cohesive design system that could be maintained and evolved independently.

## Decision
Adopted the Forest Design System (@forest-ds/core) with Tailwind CSS v4:
- Light-mode only design language
- Custom color palette (Forest, Pine, Moss, Fog, Evergreen)
- Typography: Sora (display), DM Sans (body), JetBrains Mono (code)
- Component library with BEM-adjacent naming

## Consequences
- **Positive:** Consistent UI, faster development, brand alignment
- **Positive:** Reduced CSS bundle (no Bootstrap)
- **Negative:** Migration effort for existing components
- **Negative:** Team must learn Forest DS conventions
