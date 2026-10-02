# UPSTREAM — ChainForgeLegend (preserved from upstream)

This document preserves the **original upstream project** — ChainForgeLegend,
by harutosati — faithfully, with no Quilt framing imposed. If you want
the original, **read this first**. The Quilt layer (added by SuperInstance)
is documented separately in `QUILT.md`.

## Original description

> ChainForgeLegend is a real-time distributed system engine that enables
> scalable, auto-scaling processing of complex transactions. With
> ChainForgeLegend, you get a lightweight tool that stays out of your way.

## What the upstream is

- A React 18 single-page application (Create React App scaffold)
- A single container component (`ChainforgelegendContainer`) with
  add/remove list behavior
- A simulated data-fetch step (1-second `setTimeout` in `App.jsx`,
  loading spinner → resolved title + description)
- TypeScript-style project skeleton built on JavaScript
- Standard Jest/React-Testing-Library test setup (`App.test.js`)

## What the upstream does

A minimal but complete React app demonstrating:
- Component composition (`App` → `ChainforgelegendContainer`)
- State management with `useState`
- Side effects with `useEffect`
- Conditional render (loading state vs loaded state)
- Item-list CRUD pattern (add text item, render list, remove by id)
- Form handling (controlled input + Enter-key submission)

## How the upstream works

```
src/
├── App.css                     — App-level styles (header, spinner)
├── App.jsx                     — Top-level component, simulated fetch
├── App.test.js                 — Default CRA test (renders without crash)
└── components/
    ├── ChainforgelegendContainer.css
    └── ChainforgelegendContainer.jsx
                                — Item-list CRUD container
public/
└── index.html                  — Root HTML template
package.json                    — React 18.2 + react-scripts 5.0.1
tsconfig.json                   — TypeScript config (project typed as TS)
```

### Item-list data flow

1. User types in `<input>` → `inputValue` state updates
2. User hits Enter or clicks Add → `handleAdd` fires:
   - Validates non-empty
   - Appends item with `id: Date.now()` and ISO timestamp
   - Clears input
3. Each item renders as a `<div className="item">` with text + Remove button
4. Remove → `handleRemove(id)` filters items by id

## Quick start (original)

```bash
git clone https://github.com/SuperInstance/ChainForgeLegend-Quilt.git
cd ChainForgeLegend-Quilt
npm install         # react 18, react-dom 18, react-scripts 5
npm start           # opens browser at http://localhost:3000
npm test            # runs App.test.js
npm run build       # production build to build/
```

## Credits and license

- **Upstream author:** harutosati
  ([harutosati/ChainForgeLegend](https://github.com/harutosati/ChainForgeLegend))
- **Upstream license:** MIT (preserved in `LICENSE`)
- **Quilt elevation:** SuperInstance (added the cell-graph projection layer)
- **Quilt layer license:** MIT (added as `LICENSE-QUILT`)

## Notes on the fork

- **Date imported:** 2026-09-15
- **Preserved:** All upstream code (App, components, CSS, package.json,
  tsconfig.json, test). Nothing upstream was modified.
- **Added:** `QUILT.md` (the cell-graph projection), `PLAIN_LANGUAGE.md`
  (captains-and-mechanics version), and an updated landing-page README.
  No upstream file was renamed or moved.

---

For the **Quilt projection layer** that makes this program **visible as a
cell-graph**, see `QUILT.md`. For the **plain-language version** that
explains what this does for working people, see `PLAIN_LANGUAGE.md`.
