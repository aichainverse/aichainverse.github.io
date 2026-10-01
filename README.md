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

- `_config.yml`: site title, tagline, social links, plugins
- `index.html`: home page
- `guides/index.html`: guides listing
- `_guides/<slug>.md`: long-form guides and tutorials, published at `/guides/<slug>/`
- `blog/index.html`: blog listing
- `_posts/YYYY-MM-DD-slug.md`: blog posts, published at `/blog/YYYY/MM/DD/slug/`
- `_layouts/`, `_includes/`: page shell, header, footer
- `assets/css/style.css`: styles (brand palette tokens at the top)
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
