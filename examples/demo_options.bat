@echo off
rem Stage 1: all parameters and an error in each of them.
cd /d "%~dp0.."
set URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
call run.bat --package bash --repository %URL%
call run.bat --package A --repository test_repos\diamond.txt --test-mode --output out.svg --max-depth 2 --filter X
call run.bat --repository %URL%
call run.bat --package "Bad Name" --repository %URL%
call run.bat --package bash
call run.bat --package bash --repository ftp://example.com/Packages
call run.bat --package A --repository no_such_file.txt --test-mode
call run.bat --package a --repository test_repos\diamond.txt --test-mode
call run.bat --package bash --repository %URL% --output graph.png
call run.bat --package bash --repository %URL% --output no_such_folder\graph.svg
call run.bat --package bash --repository %URL% --max-depth 0
call run.bat --package bash --repository %URL% --max-depth abc
call run.bat --package bash --repository %URL% --filter "a b"
