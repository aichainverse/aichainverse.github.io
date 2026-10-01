# aichainverse.github.io

Jekyll source for https://aichainverse.github.io, built and served by GitHub Pages from `main`.

## Local preview

Runs in Docker (no local Ruby needed) at http://localhost:4000, with live reload:

```bash
docker run -d --name aichainverse-preview -p 4000:4000 -p 35729:35729 \
  -v "$PWD":/srv/jekyll -v aichainverse-gems:/gems -w /srv/jekyll ruby:3.3 bash -c '
    cfg=_config.yml; [ -f _config.local.yml ] && cfg=$cfg,_config.local.yml
    [ -f Gemfile.local ] && export BUNDLE_GEMFILE=Gemfile.local
    bundle config set --local path /gems && bundle install --quiet &&
    bundle exec jekyll serve --host 0.0.0.0 --livereload --force_polling --config "$cfg"'
```

`docker stop aichainverse-preview` / `docker start aichainverse-preview` afterwards. Restart it after editing any config file.

### Local-only settings

Anything that must differ locally goes in gitignored files, so the live site never sees it and nothing needs stashing:

- `_config.local.yml`: merged over `_config.yml`. Nested keys merge; lists such as `plugins` replace the online list.
- `Gemfile.local` (+ its lock): used instead of `Gemfile` when present.

## Layout

| URL | Source |
|---|---|
| `/` | `index.html`: hero, then latest video / guides & tutorials / posts / open jobs (each block hides when empty) |
| `/videos/` | `_videos/<slug>.md` |
| `/learn/` | `learn/index.html`: hub linking the five sections below |
| `/guides/` | `_guides/<slug>.md` (long-form explainers) |
| `/tutorials/` | `_tutorials/<slug>.md` (step-by-step, same layout as guides) |
| `/career/` | `_career/<slug>.md` (one page per role) |
| `/glossary/` | `_data/glossary.yml` |
| `/resources/` | `_data/resources.yml` |
| `/shorts/` | `_data/shorts.yml` |
| `/jobs/` | `_data/jobs.yml` |
| `/blog/` | `_posts/YYYY-MM-DD-slug.md`, published at `/blog/YYYY/MM/DD/slug/` |
| `/about/` | `about.html` |

- `_config.yml`: site title, tagline, social links, top `nav`, collections, plugins
- `_layouts/`: `default` shell, `guide` (guides + tutorials), `video`, `career`, `post`
- `_includes/`: header, footer, cards (`post-card`, `video-card`, `job-card`), `open-jobs` (filters expired jobs), icons
- `assets/js/main.js`: guide table of contents, code copy buttons, jobs tag filter
- `assets/css/site.css`: styles, brand palette tokens at the top (not named `style.css`: the default Pages theme ships a file at that path and can overwrite it)
- `assets/img/logo.png`, `favicon.png`, `apple-touch-icon.png`: channel icon with the black background removed, generated from `assets/img/branding/profile.jpg`
- `assets/img/branding/`: original channel artwork (`profile.jpg`, `banner.jpg`), both on pure black

## Front matter

Guide (`_guides/<slug>.md`):

```yaml
---
title: Guide title
description: One-line summary shown on the card and in search results
date: 2026-10-01
updated: 2026-10-15   # optional
level: Beginner       # optional
---
```

The table of contents is built from the `##` and `###` headings, and prev/next links follow guide `date` order.

Blog post (`_posts/YYYY-MM-DD-slug.md`):

```yaml
---
title: Post title
description: Optional summary
---
```

## Pushing (aichainverse only)

`.githooks/pre-push` blocks any push unless GitHub confirms the credential belongs to the `aichainverse` account, and every pushed commit's author and committer is `335422648+aichainverse@users.noreply.github.com`. Git doesn't enable versioned hooks automatically, so after a fresh clone run:

```bash
git config core.hooksPath .githooks
git config user.name "AIChainverse"
git config user.email "335422648+aichainverse@users.noreply.github.com"
git remote set-url origin https://aichainverse@github.com/aichainverse/aichainverse.github.io.git
gh auth switch -u aichainverse   # gh serves only the active account's token
```

Tutorial (`_tutorials/<slug>.md`): same as a guide, plus optional:

```yaml
duration: 30 min
prerequisites: ["Python 3.11", "A free API key"]
```

Video (`_videos/<slug>.md`, body = notes shown under the player):

```yaml
---
title: Video title
date: 2026-10-01
youtube_id: VIDEO_ID          # from youtube.com/watch?v=VIDEO_ID
description: One-line summary
sources:                      # optional
  - { title: Source name, url: https://example.com }
---
```

Career role (`_career/<slug>.md`):

```yaml
---
title: Page title
role: Role name
description: One-line summary
skills: [Skill one, Skill two]
related:                      # optional links to guides/tutorials
  - { title: Tutorial title, url: /tutorials/slug/ }
---
```

Data files (`_data/*.yml`) each start with a commented example entry. Add entries as a YAML list:

- `glossary.yml`: `term`, `definition` (Markdown), optional `id`, `link`. Link to a term with `/glossary/#<id>`.
- `resources.yml`: `category`, `name`, `url`, optional `note`.
- `shorts.yml`: `platform` (`tiktok` or `youtube`), `url`, `title`, optional `date`.
- `jobs.yml`: `title`, `company`, `url`, optional `location`, `remote`, `posted`, `expires`, `tags`. A job is hidden once `expires` passes.

