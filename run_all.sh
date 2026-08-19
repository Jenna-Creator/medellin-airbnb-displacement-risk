#!/bin/bash
set -e

for script in scripts/*.py; do
    echo "Running $script..."
    python3 "$script"
done
