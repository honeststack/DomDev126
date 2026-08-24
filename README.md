# Astradive — AI product studio site

A static, dependency-free marketing site for an AI software agency: hero with rotating
headline, service grid, delivery-timeline accordion, animated stats, industries, client
quotes, tech stack, CTA band, contact form and footer.

Structurally modelled on the layout pattern of a modern agency homepage
(`moondive.co` was the reference for section order and information architecture).
All copy, branding, iconography, palette and code here are original — no text, logo or
asset from the reference site is reproduced. Company name, addresses, phone numbers,
emails and the headline statistics are **placeholders**: replace them before publishing.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage — hand-authored, and the source of the shared header/footer |
| `build.py` | Generates the 14 sub-pages from data structures; lifts chrome out of `index.html` |
| `assets/styles.css` | Design tokens, shared components, homepage sections, responsive + reduced-motion |
| `assets/pages.css` | Sub-page components: page hero, breadcrumbs, two-col, checklist, FAQ, roles, posts, booking, legal prose |
| `assets/app.js` | Sticky header, mobile nav, word rotator, scroll reveal, accordion, counters, marquee, slot picker, form validation |
| `assets/favicon.svg` | Logo mark as favicon |

### Generated pages

Seven service pages — `mvp-development`, `enterprise-ai-solutions`, `data-analytics`,
`cloud-engineering`, `ios-android-app-development`, `ui-ux-designing`,
`product-development` — each with hero facts, capability grid, deliverables checklist,
sticky CTA aside, FAQ and related-service links.

Plus `industries`, `careers`, `blogs`, `lets-connect`, `schedule-meeting`,
`privacy-policy`, `terms-condition`.

No framework and no runtime dependency. The only network request is Google Fonts
(Space Grotesk + JetBrains Mono); the CSS falls back to system fonts if it is blocked.

## Run it

```bash
python build.py              # regenerate all sub-pages
python build.py --list       # show target filenames only
python -m http.server 8000   # then open http://localhost:8000
```

Opening the `.html` files directly from disk also works — every link is relative.

## Editing

- **Content of a sub-page** — edit the `SERVICES` / `INDUSTRIES` / `ROLES` / `POSTS`
  dictionaries in `build.py` and re-run it.
- **Header, footer, nav** — edit `index.html`. `build.py` extracts them and rewrites
  homepage anchors (`#services` → `index.html#services`) for the sub-pages, so the two
  never drift apart. Re-run `build.py` after any chrome change.
- **A new page** — add a `build_*` function next to the existing ones and append it to
  the `written` list in `main()`.

## Customising

- **Brand name** — search `Astradive` in `index.html` (also in `<title>`/OG tags).
- **Colours** — the `:root` block at the top of `styles.css`. `--accent`, `--accent-2`,
  `--accent-3` drive the whole gradient system; changing those three re-themes the site.
- **Spacing / width** — `--shell`, `--pad`, `--section-y` in the same block.
- **Rotating headline words** — the `words` array in `app.js`.
- **Contact form** — it is a demo: `app.js` validates and clears it, nothing is sent. Add an
  `action`/`method` to the `<form>` (or POST from the submit handler) to wire up a real endpoint.
- **Stats** — `data-count` / `data-suffix` attributes on the `<b>` elements in the stats section.

## Accessibility & behaviour notes

- Skip link, landmark elements, `aria-expanded` on nav and accordion, `role="status"` on form feedback.
- `prefers-reduced-motion` disables the rotator, reveals, counters and marquee animation.
- Works without JavaScript: every section is in the HTML; only the enhancements go away.
- Mobile nav, single-column reflow and full-width buttons below 980px / 560px.
