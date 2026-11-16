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

## Languages

The site has two versions: English at `/` and Urdu at `/ur/` (right to left, Nastaliq font). They share layouts and styling but each has its own content, so one language can have pages the other lacks.

- **Interface text** (menu, buttons, empty-state lines, month names): `_data/en/strings.yml` and `_data/ur/strings.yml`, same keys in both.
- **Pages**: each section has a small file per language (`blog/index.html`, `ur/blog/index.html`) that pulls its body from `_includes/pages/`. `about.html` and `ur/about.html` hold their own text.
- **Content**: put a file in the `en/` or `ur/` folder of its collection. `_posts/ur/`, `_guides/ur/` etc. are published under `/ur/` automatically.
- **Language switch**: goes to the same page in the other language when it exists, otherwise to that language's home page. Two files are paired when they have the same name (and date, for posts), or the same `ref: some-key` in their front matter.
- **Jobs** (`_data/jobs.yml`) appear in both languages; add `lang: en` or `lang: ur` to a job to show it in one only.

## Layout

`<lang>` is `en` or `ur`; Urdu URLs are the same with `/ur` in front.

| URL | Source |
|---|---|
| `/` | `index.html`: hero, then latest video / guides & tutorials / posts / open jobs (each block hides when empty) |
| `/videos/` | `_videos/<lang>/<slug>.md` |
| `/learn/` | hub linking the five sections below |
| `/guides/` | `_guides/<lang>/<slug>.md` (long-form explainers) |
| `/tutorials/` | `_tutorials/<lang>/<slug>.md` (step-by-step, same layout as guides) |
| `/career/` | `_career/<lang>/<slug>.md` (one page per role) |
| `/glossary/` | `_data/<lang>/glossary.yml` |
| `/resources/` | `_data/<lang>/resources.yml` |
| `/shorts/` | `_data/<lang>/shorts.yml` |
| `/jobs/` | `_data/jobs.yml` |
| `/blog/` | `_posts/<lang>/YYYY-MM-DD-slug.md` (or `.html`), published at `/blog/YYYY/MM/DD/slug/` |
| `/about/` | `about.html`, `ur/about.html` |

### Medium articles

The English blog posts are generated from the Medium article folders (`article.html`, `publish.md`, images) by `scripts/import_medium.py`, which also copies the images to `assets/img/blog/<slug>/`:

```bash
uv run --with pillow scripts/import_medium.py /path/to/projects/medium /path/to/Downloads
```

To add an article, add its folder, date and any missing links to `ARTICLES` at the top of the script and run it again. It lists any link placeholders it could not fill.

- `_config.yml`: site title, tagline, social links, top `nav`, collections, plugins
- `_layouts/`: `default` shell, `guide` (guides + tutorials), `video`, `career`, `post`
- `_includes/`: `lang` and `alt` (language and translation lookup), `date`, `pages/` (section page bodies), header, footer, cards (`post-card`, `video-card`, `job-card`), `open-jobs` (filters expired jobs), icons
- `assets/js/main.js`: guide table of contents, code copy buttons, jobs tag filter
- `assets/css/site.css`: styles, brand palette tokens at the top (not named `style.css`: the default Pages theme ships a file at that path and can overwrite it)
- `assets/img/logo.png`, `favicon.png`, `apple-touch-icon.png`: channel icon with the black background removed, generated from `assets/img/branding/profile.jpg`
- `assets/img/branding/`: original channel artwork (`profile.jpg`, `banner.jpg`), both on pure black

## Front matter

Guide (`_guides/<lang>/<slug>.md`):

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

Blog post (`_posts/<lang>/YYYY-MM-DD-slug.md`):

```yaml
---
title: Post title
description: Optional summary
image: /assets/img/blog/slug/cover.jpg   # optional: card, sharing picture and cover
tags: [Tag one, Tag two]                # optional
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

Tutorial (`_tutorials/<lang>/<slug>.md`): same as a guide, plus optional:

```yaml
duration: 30 min
prerequisites: ["Python 3.11", "A free API key"]
```

Video (`_videos/<lang>/<slug>.md`, body = notes shown under the player):

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

Career role (`_career/<lang>/<slug>.md`):

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

Data files (`_data/<lang>/*.yml`, plus the shared `_data/jobs.yml`) each start with a commented example entry. Add entries as a YAML list:

- `glossary.yml`: `term`, `definition` (Markdown), optional `id`, `link`. Link to a term with `/glossary/#<id>`.
- `resources.yml`: `category`, `name`, `url`, optional `note`.
- `shorts.yml`: `platform` (`tiktok` or `youtube`), `url`, `title`, optional `date`.
- `jobs.yml`: `title`, `company`, `url`, optional `location`, `remote`, `posted`, `expires`, `tags`. A job is hidden once `expires` passes.

