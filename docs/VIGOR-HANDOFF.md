# VIGOR — design-to-code handoff

Drop this in the repo (root, or `docs/`). If you keep a `CLAUDE.md`, link to it from there so it loads automatically.

Figma file: `PmylKOrt0FztuAARUigBVO`

| What | Node | Notes |
|---|---|---|
| Design system specimen | page **From Fable**, frame `348:2` | sections 01–11: palette, semantic tokens, contrast audit, type, hierarchy, radius, elevation, spacing, interface pieces, bio modal |
| The page | page **VIGOR — v2 aligned**, frame `352:6` | desktop 1440, Bootstrap xxl grid attached |
| Bio modal | `361:2` | same page, to the right of the main frame |
| Team grid | `352:84` | 9 people, 3 × col-4 |
| Footer | `366:2` | redesigned, 4 rows + legal band |

Claude Code can read these directly through the Figma MCP — give it the file key and a node id rather than describing the design in prose.

---

## Start here

1. Replace the `:root` block in `VIGOR_Study_Ver2.html` with `vigor-tokens.css`.
2. Swap the Google Fonts `<link>` (bottom of that file — the current one is missing the italic axis and loads two weights that are no longer used).
3. Work through "Known bugs" below. They are all in the existing stylesheet and all small.
4. Then build: team grid → bio modal → footer. That order, because the modal depends on the tile markup and the footer is the only part with unresolved content.

---

## Grid

Bootstrap xxl: 1440 viewport, **1320 container**, 12 columns of 88px, **24px gutters**, **60px side margins**.

```
 1 col  88     3 col 312     6 col 648     12 col 1320
 2 col 200     4 col 424     8 col 872
```

Column width is `88n + 24(n-1)`. The 60px side margin is **grid geometry, not a spacing token** — `(1440 − 1320) ÷ 2`. Never snap it to `--space-8`.

Watch the gutter model. Those widths assume a 24px gutter. If you use a 48px gap between two columns instead (Bootstrap `g-5`), the two content boxes are 636 each, not 648. Both total 1320; they're different models. Pick one per row and be consistent.

Section layout:

| Section | Structure |
|---|---|
| Header | brand lockup / nav + CTA, space-between |
| Hero | full-container card, radius-lg, copy in cols 1–8 (872) |
| Study overview | h2 → quote deck (872) → two body columns 6+6 |
| Cards | 6 + 6 |
| Team | **3 × col-4 (424)** — see "Team count" below |
| FAQ | **col-4 heading (424) + col-8 accordion (872)** |
| Footer | identity 8 + join 4 · nav 4 × col-3 · institutional · legal band |

Two of these changed from the original: the team grid was **5 across at 20%**, which cannot land on a 12-column grid, and the FAQ was full-width, which stretched 20px questions across 1280px.

---

## Team count drives the column choice

Nine people today. Two more coming.

| People | 4-across (312) | 3-across (424) |
|---|---|---|
| 9 | 4, 4, **1** — one stranded | **3, 3, 3** ← current |
| 11 | **4, 4, 3** | 3, 3, 3, **2** |
| 12 | **4, 4, 4** | 3, 3, 3, 3 |

At 11, move back to 4-across at 312. Every portrait is at least 500px, so 312 tiles still land above 1.6×.

Current roster, in order: Garber, Harris, Pearson, Romano, Chen, Vongvirath, Atukuri, Spritz, Kwapong.

Two roles are **derived from bio text, not stated** on the live site — confirm before launch:
- **Priscilla Romano** — "Study design and oversight"
- **Rich Spritz** — "Vitiligo genetics"

Bios on the live site are **first person**. The old prototype wrote them in third person. The design uses first person; it's the client's own copy and reads warmer for recruitment.

---

## Known bugs in the current stylesheet

| Bug | Fix |
|---|---|
| `.card{background:var(--color-bg)}` — identical to the page, so cards have no surface and the shadow reads as a smudge | `var(--color-card)`. `.surface .card` then becomes redundant. |
| `.btn{font-weight:800}` | `700`. Figtree 800 is cut. |
| `h1,h2,h3{letter-spacing:-.01em}` blanket rule | Delete it; set tracking per style. It currently leaks onto the FAQ trigger via `font:inherit`, which resets family/size/weight/style/line-height but **not** letter-spacing. |
| `.card h3`, `footer h2`, `.dialog h2`, `.pull b` set no `line-height` | They inherit 1.55. The dialog name rendered 32px on 49.6px leading. Use the ramp classes. |
| Footer email is `href="#contact"` | `mailto:` |
| Footer phone is `href="#contact"` and the number is `508-555-1234` | `555` is the reserved fictional exchange. Remove until there's a real number, then `tel:`. |
| Six dead anchors: `#privacy`, `#irb`, `#consent`, `#accessibility`, `#instagram`, `#facebook` | None of these ids exist in the document. Remove or supply destinations — never substitute `#`. |
| Missing ids: `#eligibility`, `#whats-involved`, `#team`, `#faq` | Add them, or point at `#details`, `#team-h`, `#faq-h` which do resolve. |
| Sticky header overlaps anchor targets | `scroll-margin-top:96px` on in-page targets. |
| Footer link rows are 40.4px tall | 12px block padding → 44.8px. |
| Footer hover is colour-only | Add an underline on hover. |
| Media queries break at **980 / 560** | The design assumes **1200 / 768**. Reconcile, or the footer breaks at different widths from the rest of the page. |

---

## Accessibility rules that are easy to undo

- **The Join label must be pure `#FFFFFF`.** `--color-text-inverse` (#FAF7F2) on the orange is 4.24:1 and fails. Headroom on white is 4.53:1 — there is none to spare, so don't lighten the orange.
- **In the footer, the Join button needs a 2px `--color-text-inverse` keyline.** The orange is 2.27:1 against the footer blue, so the control's own boundary is invisible without it.
- **Focus rings are ground-dependent.** `--color-focus` on light, `--color-focus-inverse` on the footer / hero scrim / modal backdrop. The teal is 2.23:1 on the footer blue.
- **`--color-divider` is unusable on the footer** — it resolves to `#033688`, 1.08:1. Use `--color-border-secondary` for footer rules.
- **Don't reintroduce a 60% muted text tier.** It computes to 4.21:1 and fails. `--color-text-tertiary` is the floor.
- At 16px and 18px the large-text exemption does **not** apply. Everything needs the full 4.5:1.

---

## Bio modal

Full spec in Figma section 11. The parts that are easy to get wrong:

- Tiles must be `<button>`. That is the only reason focus can return to the right card on close.
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby` → the name element.
- Open: focus into the dialog, trap it, lock body scroll. Escape closes. Backdrop click closes — stop propagation inside the dialog.
- Close: restore focus to the triggering tile.
- Previous / Next must update **both** the counter and the `aria-labelledby` target's content. Swap the visible name but not that, and a screen reader announces the first person for the whole roster.
- Close / Previous / Next all ≥ 48 × 48.
- `prefers-reduced-motion` already has a query for `.reveal` — reuse it, don't write a second.

---

## WordPress / Carbon Fields

Field model, image sizes and the field→design mapping are in the project doc `claude/vigor-team-modal-build.md`. Short version:

- Complex field on the page template, not a CPT — the roster is fixed and lives on one page.
- `Field::make('image','portrait')->set_value_type('id')` so `wp_get_attachment_image()` gives you srcset and lazy loading.
- `add_image_size('vigor_portrait', 624, 624, true)` — covers the 312px tile at 2× and the modal's 150px portrait.
- Render the initials `<span>` only when `portrait` is empty. Don't stack it behind the image.
- Bios come from `rich_text` → print with `wp_kses_post()`, not `esc_html()`.

---

## Still unresolved — needs the client, not code

Consent form URL · privacy / data-use page · participant-rights / IRB page · accessibility statement · real phone number · verified street address · NIH grant number · IRB protocol number · whether the YouTube channel exists.

The footer degrades honestly without them: a heading earns its place only with **two or more real destinations**. Drop to 3 × col-4 (424) if the Participant Information column has none; 2 × 648 below that. Identity, Join, institutional and legal are never conditional.

One open brand question: the logo's colours (`#22418E`, `#3AB0B7`, `#7AC7CE`) are not the design system's (`#003A96`, `#009CA6`, `#9ED9DC`). The stylesheet comment says the palette was "retuned to the Mass General palette", so the divergence looks deliberate — but confirm which brand the site follows before more is built on it. Changing it later means re-auditing every contrast pair.
