# Ember Table 0.6.0

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
Import your own rulebook PDFs from either rules tab. The source PDFs and search indexes stay under the local EmberTable data folder. They are included in portable ZIP exports and are not sent to GitHub or external services. PDF imports support up to 200 MB and 2000 pages per book. Scanned books can be rendered, but text search requires a readable text layer. Books marked as removed disappear from the shelf; their copied PDF assets may remain until the data folder is manually cleaned. The two edition tabs are separate shelves, not automated rules engines. PDF.js is bundled offline during the build under its included Apache-2.0 license.

Private book packs may be imported from either rules shelf using Import book pack. This adds books without replacing campaign data. Book packs are limited to 600 MB compressed and 1 GB expanded. PDFs from local book packs are not part of the public source repository or generic installer.

## Deleting records
Campaign settings on Overview and Campaign include Delete campaign, with an exact-name confirmation. Deleting the last campaign leaves a genuinely empty workspace. Shared rulebooks stay available. Undo works during the current session, and automatic disk backups can restore older workspace revisions. Record delete buttons cover characters, journal entries, quests, sessions, NPCs, items, encounter plans/combatants, maps/tokens, wiki pages/attachments, spells/actions/resources, audio, reference entries and rolls. Deleting a character removes linked combatants and moves its items to party inventory. Removing a container leaves its contents in inventory. Attachment removal unlinks a file; its copied asset may remain on disk. Rulebook removal is separate from campaign undo.

## Book import fix in 0.6.0
The desktop book-pack button now uses the native Windows file chooser through the pywebview bridge. ZIP contents are streamed into a staging folder, checked, and installed without buffering the full pack. A persistent progress dialog shows completion or specific errors. Closing the app waits for an active import. Browser fallback uses an attached file input. Regression coverage includes the packaged EXE's actual Windows file dialog and a generated 390 MiB five-book fixture; no supplied books enter the public build runner.


## Version 0.6.0 — offline studio and campaign preparation

- Map studio: ten deterministic terrain textures, soft round brushes, size/opacity controls, thirty original canvas stamps across six categories, image stamp import, scatter, mirror, rotation, freehand paths/walls/filled shapes, labels, selection/movement and editable size/rotation/opacity. Visible layers have independent opacity, ordering and locks. Add custom layers, duplicate maps/templates, or try the starter landscape. Delete removes an entire artwork object/stroke. Maximum 5,000 artwork objects per map; battle maps remain 8–60 squares per side.
- Map PNG export at 1×/2×/4× pixel dimensions with player fog or artwork-only options. Transparent image stamps are supported. Artwork is original procedural illustration, not Inkarnate's proprietary art collection. This is a local editor, not an Inkarnate-compatible file importer.
- TV: select a connected Windows display and fullscreen/windowed player view; F11 toggles fullscreen. Rotation, scaling and a black-screen switch are in its hover toolbar. Connect HDMI or use Windows casting (Win+K) and Extend (Win+P) first. No network game server or multiplayer has been added. The Windows regression runner validates one monitor and native fullscreen; physical TVs, drivers and wireless casting require testing on the user's hardware.
- Three-step campaign setup: 2014/2024 edition, party placeholders, premise, session-zero notes and opening session. No existing campaigns are replaced.
- Five-step character builder: identity, standard array/27-point buy/manual abilities, proficiencies/features, equipment/spells, review. Twelve class starting hit dice/save proficiencies plus custom class; calculated starting HP and proficiency. Class features, legal skill selections, ancestry/background ability increases, spell levels/slots, equipment details and multiclass choices need book review. Level-up records HP, abilities, feature notes and new spells; adjust retroactive Constitution HP and resources manually.
- Bestiary: search imported PDFs and review page text/HP/AC into editable monster entries; deploy groups to encounters with linked map tokens, hidden by default, and source-page links. Extraction is page-based and can include other monsters or headers. Scanned pages require manual entry; no OCR or automatic complete structured Monster Manual database.
- Custom DM screen: choose/order party, initiative, bookmarked rules, scratchpad, quests and condition reminders.
- Relationship board: draggable original nodes, labelled edges and links to wiki/NPC/quest records. DM workspace only.
- Recaps: select journal/session/completed quest sources and assemble editable text plus checklist. This is local text assembly, not AI summarisation. Text export available.
- Diagnostics: installed version, save/import flags, disk write check, free space, backup/book counts and recent UI errors. Review/copy/export the report. Reports exclude campaign content; technical errors can still merit review before sharing.

Existing workspace and book-pack imports, native chooser regression, backups and delete controls remain covered by checks. Data format additions are backward compatible with 0.3.3 workspaces. Upgrading keeps data in the same local folder. Do not run two app versions against the same data directory simultaneously.


## Version 0.6.0 — expanded map studio and table tools

The map catalogue contains 178 original procedural stamps (including the original 30), grouped into nature, town buildings, fortifications, dungeon furnishings, wilderness, coastal and world-feature categories. There are 22 terrain palettes. Stamp search spans categories; favourites and imported image stamps stay local. This is a growing original catalogue, not Inkarnate's proprietary asset collection or file format.

New map tools include smooth editable roads/rivers, textured rectangles/ellipses/polygons, whole-layer fill, viewport panning, half-square snapping, multiple selection and marquee selection, groups, copy/paste/duplicate, rotation/scaling/mirroring, alignment/distribution, ordering within layers, reusable cross-campaign prefabs and seeded scenery generation. Generated scenes scatter editable objects; they do not automatically create a playable dungeon or enforce architectural layouts. Up to 5,000 artwork objects and 500 location pins are supported per map. Pins can link to wiki records, notes, quests, encounters or shops; hidden pins are excluded from the TV response. Shared pins under fog stay visually concealed. Player-role maps are read-only. Selection on rotated artwork uses approximate axis-aligned bounds.

Campaign search covers the active campaign and follows sharing settings. Player Overview/Campaign/Journal/Session pages now use the shared party journal rather than displaying DM quest or session text. Quest sharing stores a separate player-facing description; DM quest notes are not copied automatically. Roles remain a convenience on a shared local PC, not a login/security boundary.

Treasure and shops use whole copper arithmetic, stock limits, currency conversion and inventory transfer. Buying fails without mutation when funds or stock are insufficient. Party currency splitting leaves indivisible copper with the party. Treasure parcels can only be claimed once; Undo can restore a previous state. Wishlists are shared party records.

Downtime tracks table-agreed workdays and costs, charges the selected payer and advances the campaign calendar for each workday. Faction reputation supports private or shared records. These tools do not adjudicate official crafting or downtime rules automatically.

Combat helpers track concentration checks after damage, sustained-effect duration at the creature's next turn, reaction availability and legendary-action counters. Constitution saves use sheet modifiers or an editable NPC bonus; the player/DM resolves the result and other class features manually. Reactions and legendary action counters reset at that creature's turn. Initiative-linked resources, reminders and concentration persist in the workspace.

Local PDF exports create paginated documents/letters or reference-card sheets from reviewed text, using bundled ReportLab and embedded Bitstream Vera fonts. Spell and item cards contain your entered data. They are not a bundled official card collection. Session utilities include a wall-clock session timer, a break reminder while the app is open, checklists, original inspiration prompts and equal-probability custom roll tables.

Folder backups use a native destination-folder chooser, atomic copies and unique filenames, without overwriting earlier backups. The last successful copy is recorded; the app cannot verify whether a chosen folder is a different physical drive. Browser fallback offers a download rather than marking an external copy complete. Workspace ZIP restore supports 600 MB compressed / 1 GB expanded, allowing the existing five-book library to fit within its restore limit. Exporting still requires enough RAM and disk space for the complete local package.

Validation includes the original storage/engine/UI/native-import regressions, pure currency and concentration checks, PDF pagination/embedded-font tests, atomic folder-copy tests, a full Windows UI workflow for the new tools and the packaged application's PDF generator and player display. Physical TV hardware and Windows wireless casting remain user-hardware checks.

Concentration DCs follow the selected character/campaign edition: the 2024 calculation caps at DC 30; the 2014 calculation remains uncapped. Reference checked against the official 2024 Basic Rules glossary: https://www.dndbeyond.com/sources/dnd/br-2024/rules-glossary#Concentration. Workspace reads and writes share a lock to prevent recovery from an older snapshot during concurrent saves. Failed unchanged snapshots can be retried from Diagnostics; the desktop close handler also waits for an unresolved save failure.

### 0.6: generators, living world, streaming dice and reliable exit

Use **Generators** to select a male/female/random NPC, a job (including no job or custom), and everyday/trained/veteran experience. Review and edit the name, notes, six ability scores, HP, AC, speed, skills and attack before saving. Generated statistics are original homebrew suggestions, not official stat blocks. Saved NPCs can be added to initiative. Place generation supports towns, villages, cities, taverns, forests, mountains, rivers, ruins, islands, dungeons, roads and castles. DM locations save privately to the wiki; players can save names to their journal.

**World ledger** tracks events, rumours, objectives, contacts and threat clocks with campaign days, statuses and links to NPCs, wiki entries, quests and factions. DM notes and rumour truth are separate from player-facing text. Entries are private until explicitly shared. Shared updates appear in the player journal and campaign search. Player mode is a local convenience, not access control against someone with access to your computer or data files.

**Dice → Open dice window** opens a separate native controller. Thrown dice tumble, bounce and slide before settling; the animation presents the same cryptographic result saved in history and never determines a second result. This is an animated presentation, not a rigid-body physics simulation. Up to 16 dice are drawn, with the complete roll recorded in history. Nonstandard dice use a generic polyhedron and the exact result label.

**Dice → OBS setup** provides the current loopback-only Browser Source URL. Keep Ember Table open; in OBS select Browser Source, disable Local file, use that URL at 1280×720/60FPS and retain the default transparent CSS. The source has a transparent background, like a PNG cutout; no chroma key is needed. Broadcasting is off by default. Enable it in the controller, enable all-roll broadcasting in the main Dice page, or explicitly broadcast the last roll. Labels and totals are included. Clear overlay removes the roll immediately; rolls expire after 15 seconds. OBS uses port 17861 normally, or an available fallback if occupied. Check the displayed URL after restarting. The OBS server serves only the overlay assets and explicitly published ephemeral result, and cannot read campaign records or accept writes. It is local to the same PC; no LAN or online play is added.

Closing now returns immediately from the native Windows closing callback and performs its save check on a worker thread. The app flushes the scratchpad and waits for pending saves/imports/backups. A responsive close dialog offers Keep working or an explicit exit without waiting. Save failures remain visible, with an option to keep working and retry. Closing the main window also closes its map and dice windows.

The original D20/flame/quill icon is embedded in the executable and installer, and used for desktop/Start menu shortcuts. The installer selects a desktop shortcut by default. Builds include version/product information, use a normal directory bundle, require no elevation, and use no UPX, obfuscation or antivirus exclusions. The EXE and installer are currently **unsigned**: no publisher code-signing identity is available in this project. SmartScreen reputation and antivirus verdicts cannot be guaranteed by source changes. A public release should use a trusted Authenticode certificate or signing service, sign the application and installer, timestamp signatures, and submit any actual false positive to the detecting vendor with its precise detection name and file hash. Do not disable antivirus to install the app.
