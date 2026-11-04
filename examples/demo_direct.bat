@echo off
rem Stage 2: direct dependencies from the real Ubuntu repository.
cd /d "%~dp0.."
set URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
call run.bat --package bash --repository %URL%
call run.bat --package curl --repository %URL%
call run.bat --package no-such-package --repository %URL%
call run.bat --package bash --repository http://archive.ubuntu.com/ubuntu/no-such-file
