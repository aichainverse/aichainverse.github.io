---
name: publish-site
description: Commit and publish aichainverse.github.io changes to the live GitHub Pages site while keeping local-only preview settings out of the commit. Use when the user asks to commit, push, publish, deploy or "make it live", or asks how local and online configuration are kept apart.
---

# Publish aichainverse.github.io

The live site is GitHub Pages building `main` / root with the `github-pages` gem and only `_config.yml`.
The local preview (Docker container `aichainverse-preview`, see README "Local preview") additionally loads
`_config.local.yml` and, if present, `Gemfile.local`. Both are gitignored, so they never reach the live site.

## 1. Classify the working tree

```bash
git status --short
git diff
```

Every change must be one of:

- **Online**: meant for the live site. Gets committed.
- **Local-only config value** (url, plugins, incremental, analytics off…): move it out of `_config.yml` into
  `_config.local.yml` and restore the online value (`git checkout -- _config.yml` if it was the only change,
  otherwise edit it back). Gem differences go in `Gemfile.local`, never in `Gemfile`.
- **Local-only edit to any other tracked file** (fallback): stash just those paths for the duration of the publish:
  `git stash push -m "publish-site: local-only" -- <paths>`. Remember that a stash was made.

If a change's intent is unclear, ask the user before committing it. Never commit `_config.local.yml`,
`Gemfile.local` or `Gemfile.local.lock`; confirm with `git check-ignore -v` if in doubt.

## 2. Production build check

Build exactly what GitHub Pages builds: `_config.yml` only, the committed `Gemfile`, production env.

```bash
docker run --rm -v "$PWD":/srv/jekyll -v aichainverse-gems:/gems -w /srv/jekyll -e JEKYLL_ENV=production ruby:3.3 \
  bash -c 'bundle config set --local path /gems && bundle install --quiet && bundle exec jekyll build --config _config.yml -d /tmp/site'
```

Stop on any error or Liquid warning and fix it first.

## 3. Commit

The pre-push hook (`.githooks/pre-push`) rejects commits whose author or committer is not
`335422648+aichainverse@users.noreply.github.com`. Check `git config user.email` before committing.
Stage only the online changes (`git add <paths>`, or `git add -A` once step 1 left only online changes), then commit
with a message describing what changed on the site, ending with the attribution lines from the session's instructions.

## 4. Push as aichainverse

gh only serves the active account's token, and an IDE `GIT_ASKPASS` makes credential lookups hang.
Note the currently active account, switch, push, and always switch back:

```bash
prev=$(gh auth status 2>&1 | grep -B1 'Active account: true' | grep -o 'account [^ ]*' | cut -d' ' -f2)
gh auth switch -u aichainverse
GIT_ASKPASS= git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main
gh auth switch -u "$prev"
```

If the push fails, still switch back, then report the error. Do not bypass the hook.

## 5. Confirm it is live

```bash
T=$(gh auth token -u aichainverse)
for i in $(seq 1 40); do
  s=$(GH_TOKEN=$T gh api repos/aichainverse/aichainverse.github.io/pages/builds/latest --jq .status)
  [ "$s" = built ] || [ "$s" = errored ] && break; sleep 5
done
echo "$s"; GH_TOKEN=$T gh api repos/aichainverse/aichainverse.github.io/pages/builds/latest --jq .error.message
```

On `built`, fetch https://aichainverse.github.io/ (append `?v=$RANDOM` to dodge the CDN cache) and check that a
string from the change appears. On `errored`, report the message.

## 6. Restore local state

- If step 1 stashed anything: `git stash pop`. On a conflict, stop and show the user; never drop the stash.
- If any config file or `Gemfile.local` changed: `docker restart aichainverse-preview`
  (or recreate it with the README command if it does not exist).

Report: commit hash, live build status, anything moved to `_config.local.yml`, and whether a stash was used and restored.
