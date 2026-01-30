REM Forge requires a configured set of both JVM and program arguments.
REM Add custom JVM arguments to the user_jvm_args.txt
REM Add custom program arguments {such as nogui} to this file in the next line before the %* or
REM  pass them to this script directly
"C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot\bin\java.exe" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.18.2-40.2.0/win_args.txt %*
pause
