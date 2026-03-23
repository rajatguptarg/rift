# ADR-006: Kinetic Monolith Design System

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Product & Engineering

---

## Context

The Rift frontend required a visual identity that communicates precision, power, and developer-tool credibility. Standard light-mode SaaS aesthetics were deemed inconsistent with the target audience (platform engineers and developer experience teams).

The design system needed to:
- Provide consistent color tokens, typography, and spacing
- Work with Tailwind CSS (utility-first) without a separate component library
- Be implementable in a single sprint without a dedicated design team

---

## Decision

We adopt the **Kinetic Monolith** design system: a dark noir aesthetic with sharp geometric forms and kinetic accents.

---

## Design Tokens

**Color palette:**
- `background`: `#131313` — near-black page background
- `surface-container-lowest`: `#0E0E0E` — deepest surface (code panels, IDE areas)
- `secondary-fixed`: `#1C1C1C` — card surface / panel background
- `primary-container`: `#FF5543` — accent / CTA color (tomato red)
- `on-surface`: `#EAEAEA` — primary text
- `on-surface-variant`: `#888888` — secondary / muted text

**Typography:**
- Headlines: **Space Grotesk** — geometric sans, conveys engineering precision
- Body: **Inter** — neutral legibility for density
- Mono / code: **Fira Code** — ligature-enabled monospace for specs and CLI output

**Shape language:**
- Buttons/chips: `rounded-full` — pill form, kinetic feel
- Cards/panels: `rounded-none` (0px) — sharp edges, monolithic structure
- No drop shadows on cards — elevation communicated through background color differences

**kinetic-gradient plugin**: Radial `conic-gradient` from bottom-left corner with 5% `#FF5543` overlay — used on primary CTAs for the "kinetic" energy effect.

---

## Rationale

The `rounded-full` × `rounded-none` contrast creates visual tension that guides the eye: interactive elements (pills, buttons) invite clicks; structural elements (cards, panels) establish grids. This is a deliberate application of the Material You "shape as affordance" principle, adapted to a dark, high-contrast palette.

---

## Consequences

- **Positive**: Distinctive visual identity; all tokens encoded as Tailwind config — no CSS custom property spaghetti; designer-free implementation path.
- **Negative**: Dark-only; no light mode support planned. Not suitable for embedded widgets in third-party light-mode UIs.
- **Mitigation**: Design token layer in `tailwind.config.ts` can be forked for a light variant in future.
