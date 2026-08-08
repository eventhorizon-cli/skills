#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "Usage: $0 <input.mmd> <output.png|svg|pdf> [width] [scale]" >&2
  exit 64
fi

input_path="$1"
output_path="$2"
render_width="${3:-2000}"
render_scale="${4:-4}"

if [[ ! -f "$input_path" ]]; then
  echo "Input file does not exist: $input_path" >&2
  exit 66
fi

case "$output_path" in
  *.png|*.svg|*.pdf) ;;
  *)
    echo "Output extension must be .png, .svg, or .pdf: $output_path" >&2
    exit 64
    ;;
esac

if [[ ! "$render_width" =~ ^[0-9]+$ ]] || (( render_width < 320 )); then
  echo "Width must be an integer greater than or equal to 320." >&2
  exit 64
fi

if [[ ! "$render_scale" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Scale must be a positive number." >&2
  exit 64
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
config_path="$skill_dir/assets/mermaid.config.json"
macos_puppeteer_path="$skill_dir/assets/puppeteer.macos.json"

mkdir -p "$(dirname "$output_path")"

command_args=(
  -y @mermaid-js/mermaid-cli@11.12.0
  -i "$input_path"
  -o "$output_path"
  -b white
  -w "$render_width"
  -s "$render_scale"
  -c "$config_path"
)

if [[ -n "${MERMAID_PUPPETEER_CONFIG:-}" ]]; then
  command_args+=( -p "$MERMAID_PUPPETEER_CONFIG" )
  npx "${command_args[@]}"
elif [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  command_args+=( -p "$macos_puppeteer_path" )
  env PUPPETEER_SKIP_DOWNLOAD=true npx "${command_args[@]}"
else
  npx "${command_args[@]}"
fi

if [[ ! -s "$output_path" ]]; then
  echo "Renderer did not create a non-empty output: $output_path" >&2
  exit 1
fi

echo "Rendered $output_path"
