# Ember Table 0.3

An offline Windows campaign companion for dungeon masters and players.

## Included
- Animated 3D dice tray with modifiers, advantage/disadvantage, history, colour, reduced-motion support and damage application.
- Editable character sheets, ability/skill/save rolls, attacks, spells, slots, rest resources, temporary HP, conditions and death saves.
- Local character-sheet PDF extraction with review and updates that keep existing notes.
- Multiple battle maps with imported backgrounds, terrain/room painting, drawing layers, tokens, fog, measurement, PNG export and a separate player-display window.
- Encounter plans, monster groups, initiative, timed effects and character HP synchronization.
- Permanent 5e (2014) and revised 5e/5.5e (2024) rulebook tabs with locally imported PDFs, offline PDF.js rendering, search, bookmarks and remembered page positions. Books are shared across all campaigns on this PC, not distributed in the installer.
- Linked wiki with backlinks and attachments, session workspace, campaign calendar/travel/weather, inventory/containers/currency and local audio.
- Automatic atomic saves, 30 disk backups, recovery, 25-step undo/redo and ZIP exports containing local assets.

## Install
Download the setup executable from the latest successful **Build Windows installer** Actions run. It bundles Python. Windows 10/11 x64 and Microsoft Edge WebView2 Runtime are required. The installer is unsigned. The app does not call online services. Audio/image/PDF files you import are copied to local app storage.

Data: `%LOCALAPPDATA%/EmberTable/`. Install updates normally; they use the same data directory. Back up before upgrading. Use one instance at a time. Uninstall leaves campaign data in place.

## Build
On Windows, install Python 3.10+ and Inno Setup 6 and Node.js, then run `Build-Windows.bat`. Or push to main/run the GitHub Actions workflow. Build dependencies require internet; installed app usage does not.

## Scope and limits
This is a broad early release, not a complete automated D&D rules engine. The reference library is for your own material; commercial books and a full official rules database are not bundled. PDF layouts vary: review imported fields. Scans need manual entry; OCR is not included. Imported spells/features are retained as text, then configured as actions or spells manually. Upcasting, spell effects, hit-die healing, encumbrance/attunement rules and encounter difficulty are adjudicated manually. Fog is painted by hand; dynamic lighting/line of sight and multiplayer are not included. Terrain backgrounds are fitted to the grid; there is no image crop/calibration tool yet. DM/player modes are local workspaces, not separate secure accounts. A second monitor is selected by dragging the player window there. Calendar days are a continuous counter with editable season/year labels. ZIP imports are limited to 250 MB compressed and 500 MB expanded. Asset files not currently referenced may also be included in an export. Undo lasts only for the current app session.

## Checks
The workflow runs storage/recovery/PDF/archive tests, calculation tests, browser interaction checks in Edge, packaging, silent install, desktop startup, save/load and uninstall-data-preservation checks.

Third-party PDF processing: pypdf (BSD-3-Clause); license in `vendor/pypdf-LICENSE.txt`.

## Rulebooks
Import your own rulebook PDFs from either rules tab. The source PDFs and search indexes stay under the local EmberTable data folder. They are included in portable ZIP exports and are not sent to GitHub or external services. PDF imports support up to 80 MB and 2000 pages per book. Scanned books can be rendered, but text search requires a readable text layer. Books marked as removed disappear from the shelf; their copied PDF assets may remain until the data folder is manually cleaned. The two edition tabs are separate shelves, not automated rules engines. PDF.js is bundled offline during the build under its included Apache-2.0 license.
