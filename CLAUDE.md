# VIGOR Study — site build

A five-year, fully remote NIH observational study of vitiligo genetics, run by UMass Chan Medical School with investigators from Mass General Brigham. Audience: patients with vitiligo (age 6+) and their family members **without** vitiligo, across the US and Canada. Primary action: Join the Study. It is **not** a clinical trial and provides no medical care.

This branch builds a **static client preview for GitHub Pages**. A WordPress theme with Carbon Fields is the eventual real build — structure partials so they port.

## Read before working

| File | What's in it |
|---|---|
| `docs/VIGOR-HANDOFF.md` | Design system, grid, Figma node ids, known bugs in the existing stylesheet, accessibility rules |
| `docs/VIGOR-STATIC-BUILD.md` | Jekyll structure, component list, build order, deploy, preview-specific rules |
| `docs/vigor-tokens.css` | The complete token layer — copy to `assets/css/tokens.css`; replaces the `:root` block in `VIGOR_Study_Ver2.html` |

`docs/` is reference material, not site content. Add it to the Jekyll `exclude` list or it gets published with the preview.

Design source of truth: Figma file `PmylKOrt0FztuAARUigBVO`. Read it directly through the Figma MCP using the node ids in `docs/VIGOR-HANDOFF.md` rather than inferring the design from screenshots.

## Non-negotiables

- **`robots.txt` + `<meta name="robots" content="noindex, nofollow">` before anything else ships.** Real investigators' names and photos and a working enrolment CTA must not be indexed. A patient finding this preview and trying to enrol is a real harm.
- **Join the Study must not point at the live enrolment endpoint** in the preview.
- Join button label is pure `#FFFFFF`. `--color-text-inverse` on the orange is 4.24:1 and fails AA.
- Focus rings are ground-dependent: `--color-focus` on light, `--color-focus-inverse` on the footer, hero scrim and modal backdrop. The teal is 2.23:1 on the footer blue.
- `--color-divider` is invisible on the footer (1.08:1) — use `--color-border-secondary` there.
- Team tiles are `<button>`, never `<div>`. Focus must return to the tile when the modal closes.
- Only the nine type styles in `vigor-tokens.css` exist. Three weights: Source Serif 600, Figtree 400, Figtree 700. Don't add a tenth style or a fourth weight.
- Only the nine spacing steps exist (`--space-1` … `--space-9`). The 60px side margin is grid geometry, not a token.
- Never substitute `#` or `javascript:void(0)` for a missing destination. Render it as non-link text with a visible marker.

## Build order

1. `_config.yml`, layout, tokens wired — deploy and confirm CSS loads at the baseurl. This is the step that fails.
2. Fix the known bugs while porting the stylesheet. Don't carry them forward.
3. Header and footer includes.
4. Team grid + `_data/team.yml`.
5. Bio modal.
6. FAQ and remaining sections.

## Content status

Nine team members confirmed from the live site; two more coming — at 11 the grid moves from 3 × col-4 back to 4 × col-3. Bios are first person, client's own copy.

Still missing from the client, all rendering as "destination needed": consent form URL, privacy/data-use page, participant-rights/IRB page, accessibility statement, real phone number, verified street address, NIH grant number, IRB protocol number.
