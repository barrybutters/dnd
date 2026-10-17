@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .build-env
if errorlevel 1 goto fail
.build-env\Scripts\python.exe -m pip install pyinstaller pywebview pypdf
if errorlevel 1 goto fail
.build-env\Scripts\python.exe -m PyInstaller --clean --noconfirm EmberTable.spec
if errorlevel 1 goto fail
set "EMBER_ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%EMBER_ISCC%" set "EMBER_ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%EMBER_ISCC%" (
 echo App built in dist\EmberTable. Install Inno Setup 6 to create the installer, then rerun.
 pause
 exit /b 1
)
"%EMBER_ISCC%" installer.iss
if errorlevel 1 goto fail
echo Installer created: installer-output\EmberTable-Setup-0.2.0.exe
pause
exit /b 0
:fail
echo Build failed. Review the error above. No verified installer was produced.
pause
exit /b 1
