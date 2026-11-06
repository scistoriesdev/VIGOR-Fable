# VIGOR — static build brief (GitHub Pages)

Instructions for Claude Code. Read alongside `docs/VIGOR-HANDOFF.md` (design system, grid, known bugs, a11y rules) and `docs/vigor-tokens.css`.

---

## Target and constraint

GitHub Pages serves **static files only**. No PHP at request time, so the WordPress/Carbon Fields model in `claude/vigor-team-modal-build.md` does **not** apply to this build. It still applies to the eventual theme — so build the partials here to map 1:1 onto WordPress template parts, and porting becomes mechanical instead of a rewrite.

## Use Jekyll

GitHub Pages builds Jekyll natively — no Action, no workflow file, no local toolchain. Anything else (Eleventy, Astro, Vite) needs a GitHub Actions deploy, which is more moving parts than this site warrants.

If a no-build setup is genuinely wanted instead, the only real option is Web Components (`<vigor-header>` as a custom element). Don't. The content would mount after JS runs, which is bad for a study site that needs to be indexed and reachable without scripts. Jekyll renders real HTML at build time.

```
/
├── _config.yml
├── _layouts/
│   └── default.html          → full page shell: <head>, header, {{ content }}, footer
├── _includes/
│   ├── header.html           → navbar          → WP header.php
│   ├── footer.html           → footer          → WP footer.php
│   ├── team-grid.html        → team section    → WP template-parts/team-grid.php
│   ├── team-card.html        → one tile        → WP template-parts/team-card.php
│   ├── bio-modal.html        → modal shell     → WP template-parts/bio-modal.php
│   ├── faq.html              → accordion       → WP template-parts/faq.php
│   └── cta-join.html         → the Join button, used in 4 places
├── _data/
│   ├── team.yml              → the 9 people    → WP Carbon Fields complex field
│   └── faq.yml               → the 6 questions
├── assets/
│   ├── css/tokens.css        → vigor-tokens.css, unmodified
│   ├── css/site.css          → everything else
│   ├── js/modal.js
│   └── img/
└── index.html                → layout: default, section includes only
```

The rule: **`index.html` contains no markup of its own.** It is a list of includes. That is what makes the WordPress port a find-and-replace.

## _config.yml

```yml
title: VIGOR Study
description: A five-year, fully remote NIH study of what triggers vitiligo.
baseurl: "/REPO-NAME"      # "" if served from a user/org root domain
url: "https://USER.github.io"
sass: { style: compressed }
exclude: [README.md, LICENSE, CLAUDE.md, docs/]   # docs/ is reference material — never publish it
```

**The baseurl gotcha.** Served from `user.github.io/repo`, every root-relative path (`/assets/css/tokens.css`) 404s. Use the filter on every asset and internal link:

```liquid
<link rel="stylesheet" href="{{ '/assets/css/tokens.css' | relative_url }}">
```

Not `{{ site.baseurl }}/assets/...` — `relative_url` handles the empty-baseurl case correctly. This is the single most common way a Pages deploy looks broken when the build succeeded.

## _data/team.yml

Mirror the Carbon Fields field names exactly, so the WordPress port is a loop swap and nothing else:

```yml
- name: "Manuel Garber, PhD"
  role: "Co-lead investigator"
  institution: "UMass Chan Medical School"
  initials: "MG"
  portrait: "/assets/img/team/garber.jpg"
  bio: >
    As a co-lead investigator of this study, I am a computational biologist...
```

Fields: `name`, `role`, `institution`, `initials`, `portrait`, `bio` — identical to the Carbon Fields sub-fields.

```liquid
{% for person in site.data.team %}{% include team-card.html person=person index=forloop.index0 %}{% endfor %}
```

Later in WordPress that becomes `foreach ( carbon_get_post_meta( get_the_ID(), 'vigor_team' ) as $i => $person )` over the same keys.

Bios are **first person** — client's own copy from the live site. Don't rewrite to third person.

## Components to build

| Include | Notes |
|---|---|
| `header.html` | Logo (full colour), nav, Join CTA. Nav is `<nav aria-label="Main">`. Sticky — pair with `scroll-margin-top:96px` on anchor targets. |
| `footer.html` | 4 rows + legal band. `<footer id="contact" role="contentinfo">`. Each nav group is `<nav aria-labelledby>`. **Use the reversed logo** — the dark wordmark is 1.56:1 on the footer blue and the neuron body is 1.08:1. |
| `cta-join.html` | Accepts a `size` param (`m` default, `l` for the wide CTA) and `variant` (`footer` adds the 2px keyline). Used in header, hero, mid-page and footer — one include, not four copies. |
| `team-card.html` | A `<button>`, not a div. Carries `data-index`. Renders the initials span **only** when `portrait` is empty. |
| `bio-modal.html` | **One instance** for the whole page, not one per person. JS swaps content from a JSON blob emitted from `_data/team.yml`. |
| `faq.html` | `<button aria-expanded>` + panel. Loop `_data/faq.yml`. |

## Build order

1. `_config.yml`, `default.html`, tokens.css wired up — confirm a bare page deploys and the CSS actually loads at the baseurl. Do this first; it is the step that fails.
2. Fix the known bugs from `docs/VIGOR-HANDOFF.md` while porting the stylesheet. Don't carry them forward.
3. `header.html` + `footer.html`.
4. `team-grid.html` + `team-card.html` + `_data/team.yml`.
5. `bio-modal.html` + `modal.js`.
6. `faq.html`, remaining sections.

## Deploy

Settings → Pages → Source: **Deploy from a branch**, pick the branch and `/ (root)`. No workflow file needed; Jekyll is automatic.

If a `.nojekyll` file exists, **delete it** — it disables the Jekyll build entirely and Pages will serve the raw `_includes` directories.

Check after the first deploy: CSS loaded (not 404), fonts loaded, internal links resolve under the baseurl, and the team images resolve. Those four cover almost every broken Pages deploy.

## Carry over from the design

Everything in `docs/VIGOR-HANDOFF.md` still applies — grid widths, the nine type styles, the spacing scale, the a11y rules. The ones most likely to get lost in a static port:

- Join label must be pure `#FFFFFF`. `--color-text-inverse` on the orange is 4.24:1 and fails.
- Focus rings are ground-dependent: `--color-focus` on light, `--color-focus-inverse` in the footer, hero and modal backdrop.
- `--color-divider` is invisible on the footer (1.08:1) — use `--color-border-secondary`.
- Team tiles must be `<button>` so focus returns correctly when the modal closes.
- Previous/Next in the modal must update the `aria-labelledby` target's content, not just the visible name.

## This is a client preview — four things that follow

**1. Keep it out of search engines.** Not optional. This is a real NIH study, with real investigators' names and photographs and a working "Join the Study" button. If a patient finds the preview through Google and tries to enrol, that is a live harm — not a theoretical one. Two layers, because `robots.txt` is only advisory:

```
# robots.txt at the repo root
User-agent: *
Disallow: /
```

```html
<!-- in _layouts/default.html <head> -->
<meta name="robots" content="noindex, nofollow">
```

The meta tag is what actually keeps it out of most indexes. Do this in step 1 of the build, not at the end.

**2. Mark it visibly as a preview.** A persistent band above the header — not dismissible, not a toast. Build it from existing tokens:

```
background: var(--color-surface); color: var(--color-text);
padding: var(--space-3) var(--space-5); font: the .t-ui-small ramp
"Design preview — not the live VIGOR study site."
```

Anyone who receives the link out of context should know within one second what they are looking at.

**3. Unresolved links must not be dead links.** In a preview, a link that goes nowhere reads as a build bug, and the client will not realise the *content* is what's missing. Render anything without a destination as non-link text plus a visible marker:

```liquid
{% if item.url %}<a href="{{ item.url | relative_url }}">{{ item.label }}</a>
{% else %}<span class="pending">{{ item.label }} <em>— destination needed</em></span>{% endif %}
```

That converts a defect into a request. It is the fastest way to get the consent form URL, the privacy page, the IRB page, the accessibility statement, the real phone number, the grant number and the IRB protocol number out of UMass Chan.

**4. Decide what "Join the Study" does here.** Pointing it at the real enrolment endpoint means a stakeholder clicking through a design review can generate a real enrolment in a live NIH study. For the preview, make it a non-navigating button with a note, or have it open the URL in a new tab behind a confirm. Don't wire it straight through by default.
