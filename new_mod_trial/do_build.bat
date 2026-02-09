@echo off
dir "C:\Program Files\Microsoft" > build_output.txt 2>&1
echo --- >> build_output.txt
dir "C:\Program Files\Java" >> build_output.txt 2>&1
echo --- >> build_output.txt
where java >> build_output.txt 2>&1
