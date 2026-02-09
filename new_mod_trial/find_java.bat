@echo off
echo SCANNING JAVA > java_info.txt
dir "C:\Program Files\Microsoft" >> java_info.txt 2>&1
echo === >> java_info.txt
dir "C:\Program Files\Java" >> java_info.txt 2>&1
echo === >> java_info.txt
where java >> java_info.txt 2>&1
echo === >> java_info.txt
echo JAVA_HOME=%JAVA_HOME% >> java_info.txt
