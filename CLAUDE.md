# CLAUDE.md

Personal site of Asad Ahmed: an **online CV** (`/`) and **freelance robotics services** (`/services`). GitHub Pages user site, repo `asad-ahmed-pk/asad-ahmed-pk.github.io`, public at `https://asad-ahmed-pk.github.io/`. Same stack and rules as `~/Developer/hosting/glitch_leopard_studios_site`, minus Cloudflare.

## Hard rules
- **No Node, npm or build framework.** Tailwind v4 standalone CLI + vanilla JS. New tools or libraries: ask first.
- `site/` is exactly what gets published. Nothing secret, no docs, no sources in it. The repo is public.
- Never edit `site/assets/css/site.css` by hand; run `tool/build.sh` and commit it with the HTML/CSS that changed it.
- No third-party requests from pages: no CDNs, Google Fonts, embeds or trackers. No cookies.
- Tokens only: colours, fonts, easings from `@theme` in `src/input.css`. No hex in HTML except `theme-color`; no inline `style=` (check.py enforces). Hex is allowed in generated SVG (`scan.svg`, `favicon.svg`), kept in sync with the tokens.
- Accessibility: one `<h1>` per page, `alt` + `width`/`height` on every `<img>`, visible focus, AA contrast, animation off under `prefers-reduced-motion`, works with JS off (`[data-js-only]` hides JS-only controls).
- Header and footer markup identical on every page (check.py; only `aria-current` may differ). Nav links are absolute (`/#experience`) so they work from any page.
- Clean URLs (`/services`, not `/services.html`); GitHub Pages resolves them.
- English only.
- License: CC BY-NC-ND 4.0 (`LICENSE`), Lucide icons excepted (ISC). Keep both notices when adding third-party material.

## Content
- Source of truth for CV facts: `~/Developer/job_hunt_workspace/src/resume/robotics.tex`. Don't invent numbers, employers or claims; derived stats must be traceable to it.
- Public contact: email `asad.ahmed.de@gmail.com` and GitHub only. The phone number from the LaTeX CV is deliberately **not** published.
- Print stylesheet (bottom of `src/input.css`) turns the page into an A4 CV; check print preview after layout changes.

## Commands
- Dev: `tool/dev.sh` (port 8126) or `preview_start` with `site`.
- Build CSS: `tool/build.sh`. Check: `python3 tool/check.py` (`SKIP_CSS=1` skips the Tailwind freshness check; CI uses it).
- Hero art: `python3 tool/make_scan.py` regenerates `site/assets/img/scan.svg`.
- Link-preview images: `python3 tool/make_og.py` renders `og/card.html` (variants `#cv`, `#services`) with headless Chrome into `site/assets/img/og-{cv,services}.jpg` (1200x630). Re-run when the name, role or rate changes; the rate is on the services card.
- Deploy: push to `main` (`.github/workflows/pages.yml`; Pages source must be "GitHub Actions"). Agents never push unless asked.

## Identity
Robot's-eye view: graphite ground, lidar cyan, signal amber, ROS TF axis colours (x red, y green, z blue) as signature (brand mark = coordinate frame). Motifs: point-cloud scan with rotating sweep (`.scan`), topic-style section labels `/experience` (`.eyebrow`), trajectory timeline with waypoints (`.track`/`.role`), corner-bracket panels (`.bbox`), blueprint grid (`.grid-bg`), cut-corner buttons (`.btn`). Deliberately different from Glitch Leopard's lavender/teal.

## Status
- 2026-11-22: CV page (`/`), 404, favicon, robots/sitemap, Pages workflow built. 
- 2026-11-22: deployed and live. Pages workflow is two jobs (build uploads, deploy `needs: build`): a single job raced the artifact listing ("Found 0 artifact(s)").
- 2026-11-22: `/services` page built (offers, results from the CV, clients, process, contact). Keep private pricing (floors, negotiation notes) out of this public repo. check.py (and so CI) fails on any `*-TODO` placeholder.
- Services decisions (user, 2026-11-22): offers = perception & ROS 2, C++ performance, mapping / SLAM / 3D, tech lead & tooling. Pricing = a public hourly range plus fixed-scope sprints (updated 2026-11-25). Proof = CV achievements only (no client names, no extra projects). Audience = robotics/AV startups, established robotics companies, research labs.
- Nav: Profile, Experience, Skills (CV anchors) + Services; header Contact button is a mailto so it works on every page.
- 2026-11-25: rate changed to USD 85–130 / hour, with fixed-scope sprints as the alternative (user). Added fractional technical lead offer (`/fractional` section, `/engage` with hourly / sprint / fractional), for listing on Fractional Jobs. Fractional proof uses Covolv.ai bullets from the CV only.
