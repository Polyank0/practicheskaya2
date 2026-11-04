#!/usr/bin/env bash
# Этап 1: все параметры и ошибка в каждом из них.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
show() { echo; echo "\$ ./run.sh $*"; ./run.sh "$@"; }

show --package bash --repository "$URL"
show --package A --repository test_repos/diamond.txt --test-mode --output out.svg --max-depth 2 --filter X
show --repository "$URL"
show --package "Bad Name" --repository "$URL"
show --package bash
show --package bash --repository ftp://example.com/Packages
show --package A --repository no_such_file.txt --test-mode
show --package a --repository test_repos/diamond.txt --test-mode
show --package bash --repository "$URL" --output graph.png
show --package bash --repository "$URL" --output no_such_folder/graph.svg
show --package bash --repository "$URL" --max-depth 0
show --package bash --repository "$URL" --max-depth abc
show --package bash --repository "$URL" --filter "a b"
