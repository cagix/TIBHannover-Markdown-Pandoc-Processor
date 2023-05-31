#!/bin/sh

WORKDIR=/build

$WORKDIR/pandoc-preparation.sh
if [ -n "$MD_INPUT_DIR" ]; then
  cd "$MD_INPUT_DIR" || exit 1
fi
./.pandoc-generate.sh
