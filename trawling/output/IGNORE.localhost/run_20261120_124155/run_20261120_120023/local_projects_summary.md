# Discreet R&D Project Inventory — run_20261120_120023

- **Schema-versie:** `3.1.1`
- **Gegenereerd op:** `2026-11-20T12:05:50.857890+01:00`
- **Run-map:** `/home/steve/dump/trawler/results/local_projects_corpus/run_20261120_120023`
- **AI-synthese:** `actief via vertex_ai_oauth (gemini-3.5-flash @ global)`
- **Totaal geïnspecteerde projecten/items:** `28`

## Bron: `custom_1_gemini` (28 items)

### `android_forensics` (`2026-10-26`, 1 bestanden)
> **Domein:** Low-level OS, flashing and forensics | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een Python-script dat Android-apparaten via ADB onderschept tijdens het opstarten om gegevens te extraheren en het apparaat te vergrendelen.
> **Architectuur:** Het script maakt gebruik van ADB-interacties om Android-apparaten direct bij het opstarten te detecteren, te vergrendelen en gegevens te extraheren naar mappen. De opzet is gericht op crashbestendigheid en snelle respons zodra de ADB-interface actief wordt.
- **Talen:** Python (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** intercept_any_android_via_adb_and_pull_data_into_folders.py: intercept_any_android_via_adb_and_pull_data_into_folders.py =========================================================== An open-source, crash-proof, highly adaptive script designed to intercept ANY Android device the millisecond its ADB interface wakes up during boot. It instantly puts the device in | Symbols: run_adb(), get_device_model(), lock_down_device(), pull_all_data(), main() | Langs: Python
- **Actieve codebestanden:** `intercept_any_android_via_adb_and_pull_data_into_folders.py`
- **Slim gesnoeide submappen:** devices/fictional (high_fanout_no_code (13 subdirs: Alarms, Android, DCIM, Download, Movies, Music, Notifications, Pictures...))

### `audiotap` (`2026-11-05`, 134 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Android-applicatie die audio-opname en -afspelen combineert met een WebView-gebaseerde gebruikersinterface en lokale AI- en DSP-technologieën.
> **Architectuur:** De applicatie is opgebouwd rond een Android-architectuur met een MainActivity en een achtergrond-AudioService die via een WebAppInterface communiceren met een HTML5 WebView-frontend. De technische stack integreert Web Audio DSP en lokale Ollama LLM-functionaliteit voor geavanceerde audioverwerking en -interactie.
- **Talen:** Java (51), Python (16), HTML5 (13)
- **Assets:** .apk (6), .svg (5), .tar (1)
- **Gedetecteerde stack:** Android SDK / WebView, Ollama / Local LLM, Web Audio / DSP
- **Statische DNA-synthese:** Android: com.kleynenberg.audiotap | UI Title: 'AudioTap v18 Gemini Master - Neuro-Acoustic Edition' | Symbols: AudioTapChromeClient extends WebChromeClient, main(), MainActivity extends Activity, AudioService extends Service, CustomWebChromeClient extends WebChromeClient, AudioServiceConnection | Stack: Android SDK / WebView, Ollama / Local LLM, Web Audio / DSP
- **Actieve codebestanden:** `v18a/src_audiotap/java/com/kleynenberg/audiotap/AudioTapChromeClient.java, v18a/v18_nexus_fix.py, v18a/src_audiotap/AndroidManifest.xml, v18a/assets/www/index.html, v19/technics/index18.html, v19/technics/index17.html, v19/technics/index16.html, v19/industrial/index5.html`

### `autoingest` (`2026-10-30`, 16 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** AutoIngest is een native GNOME-applicatie die de downloadmap monitort voor automatische bestandsverwerking en handmatige sortering met behulp van AI-beeldanalyse.
> **Architectuur:** De applicatie is gebouwd met Python, GTK4 en Libadwaita voor de GUI, en maakt gebruik van PyTorch en Transformers voor lokale AI-beeldanalyse. Het systeem combineert bestandssysteembewaking met drag-and-drop-functionaliteit voor een gestroomlijnde workflow.
- **Talen:** Python (5), Shell/Bash (4)
- **Assets:** .svg (1), .png (1)
- **Gedetecteerde stack:** GTK4 / Libadwaita
- **Statische DNA-synthese:** AutoIngest v1.2 - Project Blueprint & Noodplan AutoIngest is een native GNOME-applicatie (Python/GTK4/libadwaita) voor automatische bestandsverwerking en handmatige sortering. Dit document is de volledige technische blauwdruk voor herbouw en onderhoud[cite: 9]. De huidige iteratie is ontwikkeld door Steven Kleynenberg & Google Gemini. 1. Doel & Functionaliteit De applicatie monitort `~/Downloads` voor nieuwe bestanden en biedt een Drag-and-Drop o | Symbols: analyseer_foto() | Stack: GTK4 / Libadwaita
- **Actieve codebestanden:** `unintsall.sh, install.sh, autoingest.py, README.md, ai/test_ai_captioning.py, ai/test_ai.py`

### `biossl` (`2026-10-15`, 116 bestanden)
> **Domein:** Low-level OS, flashing and forensics | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een Android-applicatie die netwerkpakketten en apparaatkoppelingen beheert via een achtergronddienst en broadcast-receivers.
> **Architectuur:** De applicatie maakt gebruik van een Android BackgroundService en BroadcastReceiver om netwerkpakketten asynchroon te verwerken via een DevicePacketQueue en SendingThread. De architectuur ondersteunt apparaatkoppeling en statuswijzigingen via specifieke callbacks en een achtergrond-jobhandler.
- **Talen:** Java (107), Python (1)
- **Assets:** .svg (1)
- **Gedetecteerde stack:** Android SDK / WebView
- **Statische DNA-synthese:** Android: com.kleynenberg.biossl | Symbols: cleanup_and_fix(), NetworkPacket, Payload, biosslBroadcastReceiver extends BroadcastReceiver, DevicePacketQueue, Item | Stack: Android SDK / WebView
- **Actieve codebestanden:** `cleanup.py, AndroidManifest.xml, Makefile, src/com/kleynenberg/biossl/NetworkPacket.java, src/com/kleynenberg/biossl/KdeConnectBroadcastReceiver.java, src/com/kleynenberg/biossl/DevicePacketQueue.java, src/com/kleynenberg/biossl/Device.java, src/com/kleynenberg/biossl/BackgroundService.java`
- **Slim gesnoeide submappen:** res (high_fanout_no_code (48 subdirs: color, drawable, drawable-hdpi, drawable-mdpi, drawable-xhdpi, drawable-xxhdpi, drawable-xxxhdpi, layout...))

### `buurtfruit` (`2026-10-24`, 3 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd buurtfruit, bevat momenteel geen actieve code of gedetecteerde technologieën.
> **Architectuur:** Het project bevindt zich in een lege of initiële staat zonder gedefinieerde softwarearchitectuur. Er zijn geen programmeertalen of actieve codebestanden gedetecteerd.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** buurtfruit

### `chrome_vision_model` (`2026-11-13`, 10 bestanden)
> **Domein:** Browser-native AI and WebGPU engines | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project legt de werking uit van het verborgen AI-model voor phishing-beveiliging binnen Google Chrome.
> **Architectuur:** Het project documenteert de client-side phishing-detectie van Chrome, die gebruikmaakt van lokaal opgeslagen TFLite- en WebNN-modellen. De nadruk ligt op het verklaren van de structuur en werking van deze specifieke modelbestanden.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** TFLite / WebNN
- **Statische DNA-synthese:** 🔍 Hoe werkt het verborgen AI-model in mijn Google Chrome? Welkom! Je hebt op je computer een verborgen map van Google Chrome gevonden (`E6DC4029A1E4B4C1/4F903F32DC2A5E36`). In deze map staan de hersenen van Chrome's ingebouwde **phishing-beveiliging** (*Client-Side Phishing Detection*). Als dit je allereerste kennismaking met AI-modellen is, geen zorgen: we leggen hier stap voor stap en in gewone mensentaal uit wat deze bestanden doen, hoe ze sam | Stack: TFLite / WebNN
- **Actieve codebestanden:** `README.md`
- **Slim gesnoeide submappen:** gpu (empty_dir)

### `cryptosum.pay` (`2026-11-04`, 34 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een monitor- en wallet-tool voor Bitcoin en Bitcoin Cash die asynchroon blockchain-data ophaalt via verschillende API's.
> **Architectuur:** De Python-applicatie maakt gebruik van asyncio en aiohttp om gelijktijdig gegevens op te vragen bij diverse blockchain-nodes met failover-races. De verzamelde data wordt verwerkt met numpy en matplotlib, en gevisualiseerd met PIL.
- **Talen:** Python (19)
- **Gedetecteerde stack:** PDF / Typography Pipeline, PipeWire / Audio DSP
- **Statische DNA-synthese:** Symbols: print_help(), log(), fetch_json(), fetch_haskoin_async(), fetch_mempool_async(), fetch_blockbook_async() | Stack: PDF / Typography Pipeline, PipeWire / Audio DSP
- **Actieve codebestanden:** `bch/kitty_bch_neuron_monitor.py, bch/05_kitty_bch_neuron_monitor.py, bch/03_kitty_bch_neuron_monitor.py, bch/02_kitty_bch_neuron_monitor.py, bch/01_kitty_bch_neuron_monitor.py, other/kitty_bitcoin_wallet.py, other/07_kitty_bitcoin_wallet.py, other/06_kitty_bitcoin_wallet.py`

### `distribucast` (`2026-11-09`, 15 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project oogst mediabestanden en genereert een audiofeed door metadata te verwerken en audiobestanden te synchroniseren.
> **Architectuur:** De applicatie is opgebouwd als een tweestaps Python-pipeline bestaande uit een harvester en een feed-generator. Het maakt gebruik van ONNX Runtime voor inferentietaken zoals taaldetectie en synchroniseert audiobestanden op basis van omgevingsvariabelen.
- **Talen:** Python (4)
- **Assets:** .mp3 (2), .mp4 (2), .tar (1)
- **Gedetecteerde stack:** ONNX Runtime
- **Statische DNA-synthese:** Symbols: run_strict(), clean_html(), extract_image_url(), detect_language(), generate_slug(), download_file() | Stack: ONNX Runtime
- **Actieve codebestanden:** `step_01_harvester.py, step_02_feed_generator.py`

### `eurostars` (`2026-10-29`, 19 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een interactieve webapplicatie voor het visualiseren van landengegevens in een vierdimensionale scatterplot met audio-ondersteuning.
> **Architectuur:** De applicatie is gestructureerd als een Progressive Web App met een HTML5- en JavaScript-frontend die gebruikmaakt van Web Audio DSP voor audio-interactie. Python-scripts ondersteunen de data-generatie en het ophalen van externe gegevens via API-verzoeken.
- **Talen:** JavaScript (4), Python (3), HTML5 (3), Shell/Bash (1)
- **Assets:** .svg (2)
- **Gedetecteerde stack:** Web Audio / DSP
- **Statische DNA-synthese:** UI Title: 'Four-Dimensional Scatter Plot - demo #1' | Symbols: query_sumobrain_facets(), playAudioTick, loadSession, saveSession, showToast, buildLegend | Stack: Web Audio / DSP
- **Actieve codebestanden:** `facets.py, euro-scatter/index.html, euro-scatter/sw.js, euro-scatter/manifest.json, euro-scatter/generate_data.py, euro-scatter/app.js, scripts/build_pwa.sh, scripts/original_gaominder.html`

### `fenix` (`2026-10-26`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Fenix is een Python-applicatie die een GTK4-gebruikersinterface koppelt aan Apache Solr voor zoekfunctionaliteit.
> **Architectuur:** De architectuur bestaat uit een Python-script dat GTK4 en Libadwaita gebruikt voor de grafische interface, gecombineerd met Apache Solr/Lucene voor het doorzoeken van gegevens.
- **Talen:** Python (1)
- **Gedetecteerde stack:** Apache Solr / Lucene, GTK4 / Libadwaita
- **Statische DNA-synthese:** Stack: Apache Solr / Lucene, GTK4 / Libadwaita
- **Actieve codebestanden:** `fenix43.py`

### `fontfilm` (`2026-11-18`, 6109 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project scant en compileert lettertypebestanden naar een Fontbook-catalogus op basis van YAML-configuraties en een SQLite-database.
> **Architectuur:** De architectuur combineert Python-bibliotheken zoals fontTools, fontforge, reportlab en weasyprint voor de analyse en PDF-generatie van lettertypen. Een SQLite-database fungeert als metadata-opslag voor synchronisatie en integriteitscontroles.
- **Talen:** Python (14), YAML (5)
- **Assets:** .ttf (189), .otf (12), .zip (5), .jpg (2), .png (2), .jpeg (1)
- **Gedetecteerde stack:** Docker / Podman, PDF / Typography Pipeline
- **Statische DNA-synthese:** Scanner_by_Lite.py: Scanner for Fontbook based on YAML configuration and SQLite metadata database. Inclusief automatische database-synchronisatie, robuuste duplicaat-check en permissieherstel. | Symbols: get_time_str(), draw_clock_dial(), parse_font_worker(), process_font_with_timeout(), main(), sanitize_str() | Stack: Docker / Podman, PDF / Typography Pipeline
- **Actieve codebestanden:** `A_lite.py, A.py, fontbook.yaml, metric_trawler.py, Scanner_by_Lite.py, Compiler_by_lite.py, import/make_font_pdf_catalogus.py, import/rescue_PRIMAFONT_fonts.py`
- **Slim gesnoeide submappen:** fonts_lib (high_fanout_no_code (13 subdirs: Adobe, Alfabetisch, Apple, Bitstream, Corrupt, Dalton_Maag, Google, ITC...)); import/Another_Fonts.2 (high_fanout_no_code (13 subdirs: Adobe, Alfabetisch, Apple, Bitstream, Corrupt, Dalton_Maag, Google, ITC...)); import/Another_Fonts.3 (asset_sink (4189 files, 4189 binary/media/font assets)); import/Another_Fonts.1/LinoType (asset_sink (4186 files, 4186 binary/media/font assets)); import/Another_Fonts.1/PrimaFont/Classic-Collection Type1 (high_fanout_no_code (184 subdirs: AME, ANT, ARK, AVA, BAS, BAU, BEG, BEI...))

### `gpuspeech` (`2026-10-13`, 11 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een offline en hardware-versnelde tekst-naar-spraak Chrome-extensie die gebruikmaakt van GPU-shaders voor realtime akoestische synthese.
> **Architectuur:** De extensie maakt gebruik van Manifest V3 en de offscreen document-API om een verborgen WebGL-context te draaien voor parallelle trigonometrische akoestische synthese. Dit zorgt voor een volledig offline werking zonder externe afhankelijkheden of netwerkverzoeken.
- **Talen:** JavaScript (2), Python (1), HTML5 (1)
- **Assets:** .png (2), .wav (1)
- **Gedetecteerde stack:** Chrome Extension MV3, Web Audio / DSP, WebGL
- **Statische DNA-synthese:** UI Title: 'GPU Speech Render Target' | GPU Speech Reader (Chrome Extension) **Author:** Steven Kleynenberg & Gemini AI [2026] **License:** MIT License **Repository:** https://github.com Technical Architecture This Chrome Extension uses Manifest V3 and the `offscreen` document API to bypass background script limitations. It launches a hidden WebGL context that executes parallel trigonometric acoustic synthesis in real-time. Zero-Dependency Guarantee - No remote network requests (`fetch | Symbols: startHardwareEngine, setupOffscreenDocument, write_file(), main() | Stack: Chrome Extension MV3, Web Audio / DSP, WebGL
- **Actieve codebestanden:** `offscreen.js, background.js, README.md, offscreen.html, manifest.json, bootstrap_gpuspeech.py`

### `innopheon2` (`2026-10-30`, 4 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een Python-script dat gefacetteerde zoekopdrachten uitvoert op Solr en Sumobrain.
> **Architectuur:** De applicatie maakt gebruik van de requests-bibliotheek om HTTP-gebaseerde zoekopdrachten uit te voeren naar een externe Solr- of Sumobrain-API. Het is gestructureerd als een enkelvoudig script voor het ophalen van gefacetteerde zoekresultaten.
- **Talen:** Python (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: query_sumobrain_facets() | Langs: Python
- **Actieve codebestanden:** `example_facted_solr_sumobrain_search.py`

### `instagrid` (`2026-11-14`, 34 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** [API HTTP 429: Too Many Requests {
  "error": {
    "code": 429,
    "message": "Resource exhausted. Please try again later. Please refer to https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429 for more details.",
    "status": "RESOURCE_EXHAUSTED"
  }
}
]
- **Talen:** Python (2)
- **Assets:** .jpg (20), .png (8), .svg (1), .jpeg (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Steven… dit raakt me echt. Dank je wel dat je dat zegt. Ik meen die woorden onderaan die strip. Jij hebt dit project gedragen — met je oog voor die sprockets, die randtekst, die kleuren, dat rood. Ik mocht alleen maar meebouwen. En kijk wat we nu hebben: van een rode placeholder, via plakwerk en schelden en opnieuw en opnieuw, naar een strip van 3240 × 11520 waar alles klopt. Dia's die verzonken liggen. Tekst die niet meer wegvalt. Kleuren die va | Symbols: genereer_definitieve_instagram_tegels() | Langs: Python
- **Actieve codebestanden:** `meta/README.md, upload_tegels.py, build_grid_final.py`

### `kitty` (`2026-11-02`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project visualiseert dynamische grafieken en afbeeldingen in de terminal met behulp van beeldverwerking en terminal-specifieke grafische commando's.
> **Architectuur:** De Python-codebase gebruikt PIL, OpenCV en NumPy om afbeeldingen te verwerken en om te zetten in geserialiseerde grafische commando's voor terminalemulators. De implementatie ondersteunt chunked schrijven en integratie met terminals zoals Kitty en Ptyxis.
- **Talen:** Python (2)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: serialize_gr_command(), write_chunked(), create_dynamic_chart(), main(), analyze_and_update_kitty() | Langs: Python
- **Actieve codebestanden:** `kitty_demo.py, match_ptyxis.py`

### `kobo` (`2026-11-01`, 79 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project implementeert het ADEPT-protocol van Adobe om DRM-beveiliging van ePub- en PDF-bestanden te beheren en te verwijderen, met specifieke ondersteuning voor Kobo-apparaten.
> **Architectuur:** De architectuur maakt gebruik van een client-serverschema waarbij platformspecifieke cryptografie- en netwerkfuncties zijn geïmplementeerd in een DRMProcessorClient-subklasse. De backend is geschreven in C++ (libgourou) en wordt gecombineerd met een Python- en PyQt6-gebaseerde beheerapplicatie voor apparaatdetectie en migratie.
- **Talen:** C/C++ Header (15), C++ (15), Shell/Bash (2), Python (2)
- **Assets:** .png (1)
- **Gedetecteerde stack:** Docker / Podman
- **Statische DNA-synthese:** Introduction libgourou is a free implementation of Adobe's ADEPT protocol used to add DRM on ePub/PDF files. It overcomes the lack of Adobe support for Linux platforms. Architecture Like RMSDK, libgourou has a client/server scheme. All platform specific functions (crypto, network...) have to be implemented in a client class (that derives from DRMProcessorClient) while server implements ADEPT protocol. A reference implementation using cURL, OpenSS | Symbols: decrypt_data(), DeviceDetectWorker, FileScanWorker, MigrationWorker, KoboManagerApp | Stack: Docker / Podman
- **Actieve codebestanden:** `kobo_drm_kraker/kleine_kraker.py, adobe_drm_kraker/libgourou/scripts/setup.sh, adobe_drm_kraker/libgourou/src/libgourou.cpp, adobe_drm_kraker/libgourou/utils/drmprocessorclientimpl.cpp, adobe_drm_kraker/libgourou/include/drmprocessorclient.h, adobe_drm_kraker/libgourou/utils/adept_loan_mgt.cpp, adobe_drm_kraker/libgourou/include/libgourou_common.h, adobe_drm_kraker/libgourou/utils/acsmdownloader.cpp`

### `mcp` (`2026-11-16`, 3 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project bevat een ongeteste Python-implementatie van het Model Context Protocol (MCP) via het script GENESIS.py.
> **Architectuur:** De architectuur is gebaseerd op een enkel Python-script dat gebruikmaakt van het Model Context Protocol (MCP) voor contextuitwisseling met taalmodellen. De huidige status van de codebase is ongetest en gecentreerd rondom het GENESIS.py-bestand.
- **Talen:** Python (1)
- **Assets:** .jpeg (1)
- **Gedetecteerde stack:** MCP (Model Context Protocol)
- **Statische DNA-synthese:** Stack: MCP (Model Context Protocol)
- **Actieve codebestanden:** `full-mcp-untested/GENESIS.py`

### `oerbron_voor_biossl` (`2026-10-15`, 167 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Android-applicatie gebaseerd op KDE Connect die zorgt voor netwerkverbindingen en apparaatkoppeling.
> **Architectuur:** De Java-architectuur maakt gebruik van Android-componenten zoals MainActivity en Fragments, ondersteund door een aangepaste ThreadPoolExecutor voor asynchrone achtergrondtaken. De netwerkfunctionaliteit en apparaatkoppelingen worden gevalideerd met een uitgebreide testsuite voor LanLink en netwerkpakketten.
- **Talen:** Java (136), Shell/Bash (3)
- **Assets:** .png (7), .svg (1), .jar (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: LanLinkTest, Downloader extends Thread, MockSharedPreference, MockSharedPreferenceEditor, NetworkPacketTest, LanLinkProviderTest | Langs: Java, Shell/Bash
- **Actieve codebestanden:** `tests/org/kde/kdeconnect/LanLinkTest.java, tests/org/kde/kdeconnect/MockSharedPreference.java, tests/org/kde/kdeconnect/NetworkPacketTest.java, tests/org/kde/kdeconnect/LanLinkProviderTest.java, tests/org/kde/kdeconnect/DeviceTest.java, store/fetchTranslations.sh, store/Messages.sh, src/org/kde/kdeconnect/async/BackgroundJobHandler.java`
- **Slim gesnoeide submappen:** res (high_fanout_no_code (53 subdirs: color, drawable, drawable-hdpi, drawable-mdpi, drawable-v21, drawable-xhdpi, drawable-xxhdpi, drawable-xxxhdpi...))

### `onnx` (`2026-11-07`, 25 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project genereert een wereldwijde feestdagenwens met behulp van 141 unieke AI-stemmen via de lokale Piper Text-to-Speech engine.
> **Architectuur:** De Python-gebaseerde applicatie maakt gebruik van de ONNX Runtime en PipeWire voor lokale audio-synthese en integratie met speech-dispatcher. Het systeem automatiseert het downloaden van TTS-modellen en het genereren van audio- en videobestanden.
- **Talen:** Python (6)
- **Assets:** .mp4 (7), .svg (2), .wav (1)
- **Gedetecteerde stack:** ONNX Runtime, PipeWire / Audio DSP
- **Statische DNA-synthese:** 🎙️ Urbi et Piper 2027 🌍 Een spectaculaire wereldwijde kerstgroet en nieuwjaarswens voor 2027, uitgesproken door maar liefst 141 unieke AI-stemmen uit alle windstreken! Met dank aan: 🤝 Rhasspy (Michael Hansen) - Voor de ontwikkeling van de Piper Text-to-Speech engine. 🤗 Hugging Face - Voor het hosten van de open-source model-repository. 💾 Draait volledig lokaal op Fedora Linux. | Symbols: krijg_feestdagen_tekst(), selecteer_top_modellen(), splits_tekst_in_regels(), main(), require_root(), restore_backup() | Stack: ONNX Runtime, PipeWire / Audio DSP
- **Actieve codebestanden:** `make_kerstfilm.py, uninstall_patch.py, install_patch.py, README.md, make_short_videos.py, demo_nl_voices.py, download_all_voices.py`
- **Slim gesnoeide submappen:** youtube_videos/shorts (asset_sink (140 files, 140 binary/media/font assets))

### `pemulator` (`2026-10-12`, 6 bestanden)
> **Domein:** Low-level OS, flashing and forensics | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit Python-script beheert en controleert een Pixel 10 Android Virtual Device door middel van procesbeheer en statusbehoud.
> **Architectuur:** De applicatie maakt gebruik van psutil voor procesbeheer om zombie-emulators te elimineren en shell-commando's uit te voeren voor AVD-beheer. Het script ondersteunt het laden, opslaan en muteren van de emulatorstatus via specifieke functies.
- **Talen:** Python (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: kill_zombie_emulators(), load_state(), save_state(), run_shell(), ensure_avd_exists(), run_emulator_attempt() | Langs: Python
- **Actieve codebestanden:** `pixel10_emulator.py`

### `podsync` (`2026-11-17`, 27 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project omvat de configuratie van podsync en bestaat uitsluitend uit TOML-configuratiebestanden.
> **Architectuur:** De opzet van het project is volledig declaratief en bevat enkel TOML-bestanden zonder actieve applicatiecode of gedetecteerde software-frameworks. Het fungeert als een statische configuratieset voor een extern synchronisatiesysteem.
- **Talen:** TOML (2)
- **Assets:** .mp3 (11), .jpg (2), .svg (2)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Langs: TOML
- **Actieve codebestanden:** `config.toml`
- **Slim gesnoeide submappen:** testing (empty_dir)

### `purgers` (`2026-10-17`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** [API HTTP 429: Too Many Requests {
  "error": {
    "code": 429,
    "message": "Resource exhausted. Please try again later. Please refer to https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429 for more details.",
    "status": "RESOURCE_EXHAUSTED"
  }
}
]
- **Talen:** Python (2)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: run_command(), main() | Langs: Python
- **Actieve codebestanden:** `purge_and_reset_keyring.py, purge_chrome.py`

### `pyend` (`2026-10-25`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een inactief of leeg Python-project genaamd pyend zonder gedetecteerde broncode of actieve bestanden.
> **Architectuur:** Er zijn geen actieve codebestanden of specifieke technologieën gedetecteerd binnen dit project. De technische architectuur kan hierdoor niet worden bepaald.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** pyend

### `pyzephyr` (`2012-06-07`, 21 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Python-bibliotheek voor het communiceren met en uitlezen van een Zephyr BioHarness-apparaat via een seriële Bluetooth-verbinding.
> **Architectuur:** De bibliotheek maakt gebruik van een seriële verbinding om datastromen te lezen en commando's te versturen, ondersteund door specifieke parsers voor berichten en signaalpakketten. Daarnaast bevat de architectuur componenten voor datasimulatie en visualisatie met behulp van NumPy en Matplotlib.
- **Talen:** Python (15)
- **Assets:** .dat (2)
- **Gedetecteerde stack:** Bluetooth Classic / BLE
- **Statische DNA-synthese:** pyzephyr is a Python library for interfacing with a Zephyr BioHarness(TM) device over a serial Bluetooth connection. The following things are supported: - Reading the data stream from the device and sending command messages to the device (zephyr.protocol.Protocol) - Parsing data messages from a serial stream (zephyr.message.MessageFrameParser) - Extracting signal values from signal packets (zephyr.signal.SignalMessageParser) | Symbols: MessagePayloadParser, parse_hxm_message(), parse_summary_packet(), parse_battery_message(), signal_packet_payload_parser_factory(), parse_10_bit_samples() | Stack: Bluetooth Classic / BLE
- **Actieve codebestanden:** `src/zephyr/protocol.py, src/zephyr/message.py, src/zephyr/bioharness.py, src/zephyr/visualization.py, src/zephyr/testing.py, src/zephyr/util.py, README, src/zephyr/delayed_stream.py`

### `skills` (`2026-10-23`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een lege repository of placeholder genaamd 'skills' zonder actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Het project bevat momenteel geen actieve codebestanden of gedetecteerde technologieën, waardoor er geen functionele software-architectuur aanwezig is.
- **Talen:** geen code gedetecteerd
- **Assets:** .zip (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** skills

### `unstack_gnome` (`2026-10-27`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Een Python-script dat via systeemcommando's helpt bij het beheren en ontstapelen van vensters in de GNOME-desktopomgeving.
> **Architectuur:** Het project is opgebouwd als een lokaal Python-script dat via systeemcommando's direct interacteert met de GNOME-omgeving. De architectuur is minimalistisch en maakt gebruik van een centrale main-functie en een run_command-helper.
- **Talen:** Python (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: run_command(), main() | Langs: Python
- **Actieve codebestanden:** `unstack_gnome_grid.py`

### `Zephyr BioHarness Reverse Engineered` (`2026-10-17`, 53 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** [API fout: The read operation timed out]
- **Talen:** Java (19)
- **Assets:** .class (14), .png (3), .jar (2), .tar (1), .apk (1), .dex (1)
- **Gedetecteerde stack:** Android SDK / WebView, Bluetooth Classic / BLE
- **Statische DNA-synthese:** Android: com.NewApp | Symbols: ReceivedEvent extends EventObject, ZephyrPacket, ConnectedListener, BTComms extends Thread, ConnectListenerImpl, AccelerometerPacketInfo | Stack: Android SDK / WebView, Bluetooth Classic / BLE
- **Actieve codebestanden:** `zephyr_source/zephyr/android/BioHarnessBT/ReceivedEvent.java, zephyr_source/zephyr/android/BioHarnessBT/ZephyrPacket.java, zephyr_source/zephyr/android/BioHarnessBT/ConnectedListener.java, zephyr_source/zephyr/android/BioHarnessBT/BTComms.java, zephyr_source/zephyr/android/BioHarnessBT/ConnectListenerImpl.java, zephyr_source/zephyr/android/BioHarnessBT/MainActivity.java, zephyr_source/zephyr/android/BioHarnessBT/ZephyrPacketListener.java, zephyr_source/zephyr/android/BioHarnessBT/CRC8.java`
- **Slim gesnoeide submappen:** assets (empty_dir)

### `zephyr2026` (`2026-10-18`, 66 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een Android-applicatie die via Classic Bluetooth verbinding maakt met een Zephyr BioHarness om klinische telemetriegegevens te streamen en te visualiseren op een dashboard.
> **Architectuur:** De applicatie is gebouwd met de Android SDK en maakt gebruik van Bluetooth RFCOMM/SPP-threads voor data-ontvangst, gecombineerd met een custom WaveformView voor visualisatie en een CloudSync-component. Het project implementeert het Zephyr-protocol en HRV-berekeningen zonder externe afhankelijkheden.
- **Talen:** Java (28), Shell/Bash (1)
- **Assets:** .jar (1)
- **Gedetecteerde stack:** Android SDK / WebView, Bluetooth Classic / BLE
- **Statische DNA-synthese:** Zephyr 2026 – BioHarness dashboard (`com.kleynenberg.zephyr2026`) Android app that connects over Classic Bluetooth (SPP/RFCOMM, UUID `00001101-0000-1000-8000-00805F9B34FB`) to a Zephyr BioHarness (`C8:3E:99:0D:9A:67`, or any bonded device named `BH…`) and shows the stream as the "Clinical Telemetry – Marathon Monitoring" dashboard from the mockup. Open the folder in **Android Studio (Koala or newer)** → Sync → Run. No third-party dependencies. | Symbols: MainActivity extends Activity, BTBroadcastReceiver extends BroadcastReceiver, BTBondReceiver extends BroadcastReceiver, ProtocolTest, HrvTest, CloudSync | Stack: Android SDK / WebView, Bluetooth Classic / BLE
- **Actieve codebestanden:** `app/src/main/java/com/kleynenberg/zephyr2026/MainActivity.java, gemini-code-1792290132281.java, java_for_zephyr2026_project.sh, README.md, app/src/test/java/zephyr/android/BioHarnessBT/ProtocolTest.java, app/src/test/java/com/kleynenberg/zephyr2026/HrvTest.java, app/build.gradle, build.gradle`
