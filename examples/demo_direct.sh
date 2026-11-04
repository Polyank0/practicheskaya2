#!/usr/bin/env bash
# Этап 2: прямые зависимости пакетов из настоящего репозитория Ubuntu.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
show() { echo; echo "\$ ./run.sh $*"; ./run.sh "$@"; }

show --package bash --repository "$URL"
show --package curl --repository "$URL"
show --package no-such-package --repository "$URL"
show --package bash --repository http://archive.ubuntu.com/ubuntu/no-such-file
