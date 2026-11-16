#!/usr/bin/env bash
# Commit a tree built by build_intraday_fork.sh and push it to its repository.
#
#   bash new_pipeline/scripts/publish_intraday_fork.sh <built-tree> <remote-url>
#
# The tree is committed as ONE import commit (everything except the vault
# archives) followed by ONE commit per archive, and pushed one commit at a
# time. That shape is forced, not chosen: the 63 archives total 4.4 GB, the
# largest is 96.5 MB, and a push here has to stay under ~100 MB.
#
# Safe to re-run at any point. A tree that is already committed is not
# re-committed, and the push resumes after whatever the remote already has —
# so a dropped connection or a reclaimed container costs one archive, not the
# upload.
#
# COMMIT_TRAILER (optional) is appended to every commit message.
set -euo pipefail

TREE="${1:?usage: publish_intraday_fork.sh <built-tree> <remote-url>}"
REMOTE="${2:?usage: publish_intraday_fork.sh <built-tree> <remote-url>}"
SRC="$(git rev-parse --show-toplevel)"
PARENT="$(git -C "$SRC" rev-parse --short HEAD)"
NAME="$(git -C "$SRC" config user.name || echo Claude)"
EMAIL="$(git -C "$SRC" config user.email || echo noreply@anthropic.com)"
TRAILER="${COMMIT_TRAILER:-}"
cd "$TREE"

[ -f docs/fork/GAUNTLET.sha256 ] || {
  echo "$TREE does not look like a built fork (no docs/fork/GAUNTLET.sha256)" >&2
  exit 1
}

if [ ! -d .git ]; then
  echo "==> committing the tree"
  git init -q -b main
  git config user.name "$NAME"
  git config user.email "$EMAIL"
  git add -A -- . ':!data/minute_archives'
  git commit -q -m "Initial import: intraday research framework, forked from the daily project

Produced by the parent's build_intraday_fork.sh from its commit $PARENT.
See docs/fork/MANIFEST.md for what travelled and how it was verified,
docs/fork/KICKOFF.md for the first session's brief, and claude.md for the
ruleset and charter. The minute-vault archives follow, one commit each.

Status: research. No strategy is promoted and nothing is trading.${TRAILER:+

$TRAILER}"
  shopt -s nullglob
  for t in data/minute_archives/*.tar; do
    label="$(basename "$t" .tar)"
    git add "$t"
    git commit -q -m "Minute vault archive ${label#minute_} ($(( $(stat -c %s "$t") / 1000000 ))MB)${TRAILER:+

$TRAILER}"
  done
fi
[ -z "$(git status --porcelain)" ] || { echo "tree has uncommitted changes — refusing to publish" >&2; exit 1; }

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

# Resume after whatever the remote already holds.
have="$(git ls-remote origin refs/heads/main 2>/dev/null | cut -f1 || true)"
if [ -n "$have" ]; then
  git cat-file -e "$have^{commit}" 2>/dev/null || {
    echo "remote main ($have) is not a commit of this tree — refusing to push over it" >&2
    exit 1
  }
  range="$have..main"
else
  range="main"
fi
total="$(git rev-list --count main)"
done_n="$(( total - $(git rev-list --count "$range") ))"
echo "==> pushing $(git rev-list --count "$range") of $total commits to $REMOTE"

for sha in $(git rev-list --reverse "$range"); do
  done_n=$((done_n + 1))
  ok=0
  for wait in 0 2 4 8 16; do
    [ "$wait" = 0 ] || sleep "$wait"
    if git push -q origin "$sha:refs/heads/main"; then ok=1; break; fi
  done
  [ "$ok" = 1 ] || { echo "push failed at $done_n/$total ($sha) — re-run to resume" >&2; exit 1; }
  echo "[$done_n/$total] $(git log --format=%s -1 "$sha" | cut -c1-60)"
done

remote_head="$(git ls-remote origin refs/heads/main | cut -f1)"
if [ "$remote_head" = "$(git rev-parse main)" ]; then
  echo "ALL PUSHED — remote main = $(git rev-parse --short main), $total commits"
else
  echo "MISMATCH — remote main $remote_head vs local $(git rev-parse main)" >&2
  exit 1
fi
