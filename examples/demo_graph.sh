#!/usr/bin/env bash
# Этап 3: граф зависимостей на разных случаях тестового репозитория.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
show() { echo; echo "\$ ./run.sh $*"; ./run.sh "$@"; }

show --package A --repository test_repos/diamond.txt --test-mode
show --package A --repository test_repos/chain.txt --test-mode
show --package A --repository test_repos/chain.txt --test-mode --max-depth 2
show --package A --repository test_repos/filter.txt --test-mode
show --package A --repository test_repos/filter.txt --test-mode --filter XTRA
show --package A --repository test_repos/cycle.txt --test-mode
show --package A --repository test_repos/self_loop.txt --test-mode
show --package Z --repository test_repos/cycle.txt --test-mode
show --package A --repository test_repos/broken.txt --test-mode
show --package curl --repository "$URL" --max-depth 2
