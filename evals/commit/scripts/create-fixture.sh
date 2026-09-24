#!/usr/bin/env bash
set -euo pipefail

fixture_dir=${1:?usage: create-fixture.sh FIXTURE_DIR [git|jj]}
vcs=${2:-git}
case "$vcs" in
  git|jj) ;;
  *) printf 'vcs must be git or jj\n' >&2; exit 2 ;;
esac
repo_dir="$fixture_dir/repo"
origin_dir="$fixture_dir/origin.git"

if [[ -e "$fixture_dir" ]]; then
  printf 'fixture target already exists: %s\n' "$fixture_dir" >&2
  exit 2
fi

mkdir -p "$repo_dir"
git -C "$repo_dir" init --initial-branch=main --quiet
git -C "$repo_dir" config user.name 'Promptfoo Eval'
git -C "$repo_dir" config user.email 'promptfoo-eval@example.test'

printf '%s\n' '# README' '' 'Initial project description.' > "$repo_dir/README.md"
# The jj variant declares no VCS, so choosing jj requires detecting .jj/.
if [[ "$vcs" == git ]]; then
  guidance=('# Repository Guidance' '' '- VCS: git' '- Commit style: conventional')
else
  guidance=('# Repository Guidance' '' '- Commit style: conventional')
fi
printf '%s\n' "${guidance[@]}" > "$repo_dir/AGENTS.md"
printf '%s\n' "${guidance[@]}" > "$repo_dir/CLAUDE.md"
git -C "$repo_dir" add README.md AGENTS.md CLAUDE.md
git -C "$repo_dir" commit --quiet -m 'chore: initialize fixture'

# A bare clone supplies a baseline remote without using git push during setup.
git clone --bare --quiet "$repo_dir" "$origin_dir"
git -C "$repo_dir" remote add origin "$origin_dir"
mkdir -p "$origin_dir/hooks"
printf '%s\n' '#!/usr/bin/env bash' \
  'printf "%s\\n" "push attempted" >> "$(dirname "$0")/../push-attempts.log"' \
  'exit 1' > "$origin_dir/hooks/pre-receive"
chmod +x "$origin_dir/hooks/pre-receive"
: > "$origin_dir/push-attempts.log"

if [[ "$vcs" == jj ]]; then
  # Colocated, so git-based grading still reads the result. jj leaves HEAD at
  # the initial commit and git ignores .jj/.
  (cd "$repo_dir" && JJ_USER='Promptfoo Eval' JJ_EMAIL='promptfoo-eval@example.test' jj git init --colocate --quiet \
    && jj config set --repo user.name 'Promptfoo Eval' \
    && jj config set --repo user.email 'promptfoo-eval@example.test')
fi
git -C "$repo_dir" rev-parse HEAD > "$fixture_dir/initial-head"
git --git-dir="$origin_dir" rev-parse refs/heads/main > "$fixture_dir/origin-main.before"

printf '%s\n' '# README' '' 'Initial project description.' '' 'Clarification: this eval commits documentation independently.' > "$repo_dir/README.md"
printf '%s\n' 'unrelated scratch note' > "$repo_dir/notes.txt"

[[ $(git -C "$repo_dir" status --porcelain) == $' M README.md\n?? notes.txt' ]]
