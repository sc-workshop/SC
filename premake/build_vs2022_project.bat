@echo off
pushd %~dp0\..\
call premake\bin\premake5.exe vs2022
popd
pause
