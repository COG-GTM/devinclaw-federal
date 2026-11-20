#!/usr/bin/env bash
# Re-render the architecture diagram from its Graphviz source (needs `dot`, e.g. apt-get install graphviz).
set -euo pipefail
cd "$(dirname "$0")"
dot -Tpng -Gdpi=110 architecture.dot -o architecture.png
dot -Tsvg architecture.dot -o architecture.svg
