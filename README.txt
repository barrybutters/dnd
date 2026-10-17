EMBER TABLE — WINDOWS DESKTOP BUILD SOURCE (NOT A COMPILED INSTALLER)

Target: Windows 10/11 x64, native desktop window, offline use, bundled Python.
The final deliverable from this build is installer-output/EmberTable-Setup.exe.
Users of that installer do not need Python. Microsoft Edge WebView2 Runtime
must be installed on the destination PC. It is not bundled in this source kit.

Build machine requirements: Windows x64, Python 3.10+, Inno Setup 6, internet
for build dependencies. Run Build-Windows.bat. Dependencies are installed into
a separate .build-env folder. Build tools are only required on the build PC.

Campaigns save under %LOCALAPPDATA%\EmberTable\workspace.json, separate from
program files so app upgrades and uninstall do not delete campaign files.

This package was prepared on Linux. Syntax and local server behavior can be
checked here; the Windows build, installer, WebView2 integration, file downloads,
and PDF selection still require validation on Windows. The installer is unsigned.
No compiled .exe is included. This is the same early feature set as the local
first release, not the completed all-in-one product.

Before distributing: build on Windows, install on a clean test account, test PDF
import and review, saving after restart, map/workspace exports, restore, upgrade
and uninstall. Confirm campaign data survives upgrade and uninstall. The app
uses one local HTTP server and a desktop WebView bound to an ephemeral loopback
port. Run only one app instance at a time.

pypdf license is included in vendor/pypdf-LICENSE.txt. Review licenses for all
build dependencies before distribution. Code signing and bundling an offline
WebView2 runtime are additional release steps.

AUTOMATED BUILD
A manual GitHub Actions workflow is included at .github/workflows/windows-installer.yml.
Place this directory contents at the repository root. Run Build Windows installer
from the Actions tab. Download EmberTable-Windows-Installer when the run succeeds.
This workflow has not yet been executed. Compilation is not a substitute for
interactive testing of the installed app on Windows.
