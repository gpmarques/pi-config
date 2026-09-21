#!/bin/sh
set -eu

usage() {
    echo "Usage: $0 DIRECTORY" >&2
    exit 2
}

[ "$#" -eq 1 ] || usage
target=$1
[ -n "$target" ] || usage

script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
template=$script_dir/../templates/workspace/AGENTS.md

if [ ! -f "$template" ] || [ ! -r "$template" ]; then
    echo "Error: workspace template is missing or unreadable: $template" >&2
    exit 1
fi

if [ -e "$target" ] || [ -L "$target" ]; then
    echo "Error: target already exists: $target" >&2
    exit 1
fi

trimmed=${target%/}
workspace_name=${trimmed##*/}
[ -n "$workspace_name" ] || usage

mkdir "$target"
mkdir "$target/data" "$target/docs" "$target/projects" "$target/worktrees"

WORKSPACE_NAME=$workspace_name awk '
{
    line = $0
    token = "{{WORKSPACE_NAME}}"
    while ((position = index(line, token)) != 0) {
        line = substr(line, 1, position - 1) ENVIRON["WORKSPACE_NAME"] \
               substr(line, position + length(token))
    }
    print line
}
' "$template" > "$target/AGENTS.md"

printf 'Created workspace: %s\n' "$target"
