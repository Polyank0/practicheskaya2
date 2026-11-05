@echo off
rem Stage 3: dependency graph on different test repositories.
cd /d "%~dp0.."
set URL=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
call run.bat --package A --repository test_repos\diamond.txt --test-mode
call run.bat --package A --repository test_repos\chain.txt --test-mode
call run.bat --package A --repository test_repos\chain.txt --test-mode --max-depth 2
call run.bat --package A --repository test_repos\filter.txt --test-mode
call run.bat --package A --repository test_repos\filter.txt --test-mode --filter XTRA
call run.bat --package A --repository test_repos\cycle.txt --test-mode
call run.bat --package A --repository test_repos\self_loop.txt --test-mode
call run.bat --package Z --repository test_repos\cycle.txt --test-mode
call run.bat --package A --repository test_repos\broken.txt --test-mode
call run.bat --package curl --repository %URL% --max-depth 2
