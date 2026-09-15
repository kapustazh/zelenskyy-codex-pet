#!/usr/bin/env sh
set -eu

raw_base="${ZELENSKYY_RAW_BASE:-https://raw.githubusercontent.com/kapustazh/zelenskyy-codex-pet/main}"
codex_home="${CODEX_HOME:-$HOME/.codex}"
pet_root="$codex_home/pets"
target="$pet_root/zelenskyy"
temporary="$(mktemp -d)"
staged="$temporary/zelenskyy"
backup="$pet_root/.zelenskyy.backup.$$"
had_backup=0

cleanup() {
  rm -rf -- "$temporary"
}
trap cleanup EXIT HUP INT TERM

mkdir -p "$staged"
curl -fsSL --proto '=https' --tlsv1.2 "$raw_base/pet.json" -o "$staged/pet.json"
curl -fsSL --proto '=https' --tlsv1.2 "$raw_base/spritesheet.webp" -o "$staged/spritesheet.webp"

grep -q '"id"[[:space:]]*:[[:space:]]*"zelenskyy"' "$staged/pet.json"
grep -q '"spriteVersionNumber"[[:space:]]*:[[:space:]]*2' "$staged/pet.json"
test "$(wc -c < "$staged/spritesheet.webp")" -gt 1000

mkdir -p "$pet_root"
if [ -e "$target" ]; then
  mv -- "$target" "$backup"
  had_backup=1
fi

if mv -- "$staged" "$target"; then
  if [ "$had_backup" -eq 1 ]; then
    rm -rf -- "$backup"
  fi
else
  if [ "$had_backup" -eq 1 ] && [ ! -e "$target" ]; then
    mv -- "$backup" "$target"
  fi
  exit 1
fi

printf 'Installed Zelenskyy to %s\n' "$target"
printf 'Restart Codex, then select Zelenskyy in Settings > Pets.\n'
