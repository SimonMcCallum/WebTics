@echo off
REM Build script for WebTics Blackjack Server
REM Requires Visual Studio command line tools (cl.exe)

echo WebTics Blackjack Server - Build Script
echo =========================================

REM Check if Visual Studio tools are available
where cl.exe >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Visual Studio compiler not found!
    echo Please run this script from a Visual Studio Developer Command Prompt
    echo or run vcvarsall.bat first.
    pause
    exit /b 1
)

echo.
echo Compiling BlackjackServer.cpp...
echo.

REM Compile the blackjack server
cl /EHsc /std:c++14 /I..\..\inc ^
   BlackjackServer.cpp ..\..\src\WebTics.cpp ^
   /Fe:BlackjackServer.exe ^
   /link Winhttp.lib

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo =========================================
echo Build successful!
echo =========================================
echo.
echo Executable: BlackjackServer.exe
echo.
echo To run the server, type: BlackjackServer.exe
echo.

REM Clean up intermediate files
if exist *.obj del *.obj

pause
