#/usr/bin/bash

nix-shell -A freexgraph --run "
    coverage run -m pytest test &&
    coverage xml --omit freexgraph/*.py &&
    bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage.xml
"
