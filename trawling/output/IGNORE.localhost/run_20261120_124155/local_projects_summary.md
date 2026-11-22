# Discreet R&D Project Inventory — run_20261120_124155

- **Schema-versie:** `3.1.1`
- **Gegenereerd op:** `2026-11-20T12:48:26.101827+01:00`
- **Run-map:** `/home/steve/gemini/trawler/results/local_projects_corpus/run_20261120_124155`
- **AI-synthese:** `actief via vertex_ai_oauth (gemini-3.5-flash @ global)`
- **Totaal geïnspecteerde projecten/items:** `44`

## Bron: `custom_1_Gemini` (44 items)

### `audiotap` (`2026-10-09`, 48 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een Android-applicatie die een HTML5-gebruikersinterface in een WebView combineert met een achtergrond-audioservice voor audio-afspelen.
> **Architectuur:** De architectuur maakt gebruik van een Android MainActivity met een WebView die via een WebAppInterface communiceert met een Java-gebaseerde AudioService. Deze service maakt gebruik van MediaSession-callbacks en ondersteunt Web Audio en DSP-functionaliteiten.
- **Talen:** Python (15), Java (12), HTML5 (1)
- **Assets:** .apk (3), .svg (2), .dex (1), .jar (1)
- **Gedetecteerde stack:** Android SDK / WebView, Web Audio / DSP
- **Statische DNA-synthese:** Android: com.kleynenberg.audiotap | UI Title: 'AudioTap' | Symbols: CustomWebViewClient extends WebViewClient, CustomWebChromeClient extends WebChromeClient, PermissionGrantRunnable, MainActivity extends Activity, AudioServiceConnection, WebAppInterface | Stack: Android SDK / WebView, Web Audio / DSP
- **Actieve codebestanden:** `assets/www/index.html, src_audiotap/java/com/kleynenberg/audiotap/CustomWebViewClient.java, src_audiotap/java/com/kleynenberg/audiotap/CustomWebChromeClient.java, src_audiotap/java/com/kleynenberg/audiotap/PermissionGrantRunnable.java, src_audiotap/java/com/kleynenberg/audiotap/MainActivity.java, src_audiotap/java/com/kleynenberg/audiotap/AudioServiceConnection.java, src_audiotap/java/com/kleynenberg/audiotap/WebAppInterface.java, src_audiotap/java/com/kleynenberg/audiotap/JavascriptToggleRunnable.java`
- **Slim gesnoeide submappen:** bin/com/kleynenberg/audiotap (asset_sink (16 files, 16 binary/media/font assets))

### `bernardus` (`2026-08-20`, 21 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project vergelijkt afbeeldingen en berekent visuele kenmerken om rapportages te genereren binnen een PDF- en typografie-pijplijn.
> **Architectuur:** De applicatie is opgebouwd in Python met een Tkinter-GUI en maakt gebruik van modules voor kenmerkberekening, hash-vergelijkingen en beeldverwerking. Een Bash-script faciliteert de batch-verwerking van de gegevens voor rapportage-doeleinden.
- **Talen:** Python (7), Shell/Bash (1), YAML (1)
- **Assets:** .jpg (2)
- **Gedetecteerde stack:** PDF / Typography Pipeline
- **Statische DNA-synthese:** Symbols: read_paths(), compute_features(), compare_images(), get_sliding_color(), short_path(), format_img_uri() | Stack: PDF / Typography Pipeline
- **Actieve codebestanden:** `report/supersift.py, report/sift.py, report/report2.py, report/report.py, reverse/gui.py, matchup/gui.py, matchup/vergelijk.py, batch_verrijk.sh`
- **Slim gesnoeide submappen:** onedrive (asset_sink (70 files, 70 binary/media/font assets))

### `bookmarks` (`2026-09-05`, 14 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project analyseert de kosten en voert het geautomatiseerd clusteren van bookmarks uit met behulp van de Gemini 1.5 Pro API.
> **Architectuur:** Het project maakt gebruik van Python-scripts en de google-genai SDK om bookmarks te clusteren en API-sleutels te scannen. De architectuur omvat tevens kostenberekeningen voor het gebruik van het Gemini 1.5 Pro-model via Vertex AI.
- **Talen:** Python (6), HTML5 (2), YAML (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Kosten- en Billing-analyse: Bookmark Clustering via Gemini 1.5 Pro Deze analyse beschrijft de verwachte kosten voor het geautomatiseerd herordenen van de bookmarks via de moderne `google-genai` SDK met het Gemini 1.5 Pro model. [REDACTED_SENSITIVE_LINE] - **Aantal unieke bookmarks**: 2.158 [REDACTED_SENSITIVE_LINE] [REDACTED_SENSITIVE_LINE] 2. Prijsstelling Gemini 1.5 Pro (Vertex AI / Enterprise) [REDACTED_SENSITIVE_LINE] [REDACTED_SENSITIVE_LINE | Langs: Python, HTML5, YAML
- **Actieve codebestanden:** `scan_keys_to_tsv.py, scan_keys_apis.py, scan_keys.py, TEST.html, cluster_bookmarks.py, list_model.py, metadata.yaml, 03_schrijf_voorwoord_bijschriften_en_nawoord_met_gemini.py`

### `build` (`2026-10-09`, 12 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project genaamd 'build' bevat geen actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Er is geen actieve softwarearchitectuur of technologie gedetecteerd binnen dit project. De metadata wijst op een lege projectstructuur met de naam 'build'.
- **Talen:** geen code gedetecteerd
- **Assets:** .class (8), .zip (1), .apk (1), .dex (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** build

### `c` (`2026-02-15`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een eenvoudige Hello World-applicatie geschreven in de programmeertaal C.
> **Architectuur:** De applicatie bestaat uit een enkel C-bronbestand zonder verdere externe afhankelijkheden of complexe architectuur. Het dient als een minimale implementatie voor testdoeleinden.
- **Talen:** C (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Langs: C
- **Actieve codebestanden:** `helloworld.c`

### `cli` (`2026-03-05`, 9 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project biedt een command-line interface via een Makefile voor YouTube-gerelateerde taken.
> **Architectuur:** De architectuur is minimaal en bestaat uit een Makefile die CLI-commando's aanstuurt voor YouTube-interactie. Er zijn geen aanvullende programmeertalen of software-architecturen gedocumenteerd.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** cli
- **Actieve codebestanden:** `youtube/Makefile`

### `elro` (`2026-08-24`, 5 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project converteert een live MJPEG-stream van een ELRO-camera naar een MP4-bestand.
> **Architectuur:** De Python-applicatie gebruikt asyncio en aiohttp om de live stream asynchroon te consumeren. De ontvangen frames worden direct naar een ffmpeg-subproces gepijpt om het MP4-bestand te genereren.
- **Talen:** Python (2)
- **Assets:** .mp4 (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** ffmpeg_elro.py: ELRO MJPEG to MP4 Converter ------------------------------------------------------------------------- Leest 20 seconden de live stream uit via aiohttp en pipe't de frames rechtstreeks naar ffmpeg om een MP4-bestand te genereren. | Symbols: record_stream_to_mp4(), test_stream() | Langs: Python
- **Actieve codebestanden:** `ffmpeg_elro.py, test_elro.py`

### `eneco` (`2026-08-12`, 161 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project verwerkt en analyseert Eneco PDF- en Excel-documenten om gefilterde TSV-bestanden en visualisaties te genereren.
> **Architectuur:** De applicatie maakt gebruik van Python-scripts met pypdf en pandas om data uit documenten te extraheren, op te schonen en te exporteren naar TSV-formaat. Visualisaties worden gegenereerd met behulp van matplotlib.
- **Talen:** Python (6), HTML5 (1)
- **Assets:** .png (17)
- **Gedetecteerde stack:** PDF / Typography Pipeline
- **Statische DNA-synthese:** UI Title: 'Gmail - Jouw kopie van het chatgesprek met Eneco' | Symbols: clean_text(), parse_pdf_data(), parse_excel_data(), main(), parse_all_eneco_pdfs(), parse_eneco_pdfs() | Stack: PDF / Typography Pipeline
- **Actieve codebestanden:** `archief/eneco_totaal_script.py, archief/plotje.py, archief/eneco_pdf_naar_tsv_v2.py, archief/eneco_pdf_naar_tsv.py, archief/eneco_to_tsv.py, archief/make_tsv.py, archief/2023-2024/kopie-chatg-Eneco-24012024-18.37.html`

### `eurostars` (`2026-09-11`, 18 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een interactieve webapplicatie voor het visualiseren van landengegevens in een vierdimensionale scatterplot met audio-ondersteuning.
> **Architectuur:** De applicatie is gestructureerd als een Progressive Web App met een HTML5- en JavaScript-frontend die gebruikmaakt van Web Audio DSP voor audio-interactie. Python-scripts ondersteunen de data-generatie en het ophalen van externe gegevens via API-verzoeken.
- **Talen:** JavaScript (4), Python (3), HTML5 (3), Shell/Bash (1)
- **Assets:** .svg (2)
- **Gedetecteerde stack:** Web Audio / DSP
- **Statische DNA-synthese:** UI Title: 'Four-Dimensional Scatter Plot - demo #1' | Symbols: query_sumobrain_facets(), playAudioTick, loadSession, saveSession, showToast, buildLegend | Stack: Web Audio / DSP
- **Actieve codebestanden:** `facets.py, euro-scatter/index.html, euro-scatter/sw.js, euro-scatter/manifest.json, euro-scatter/generate_data.py, euro-scatter/app.js, scripts/build_pwa.sh, scripts/original_gaominder.html`

### `fenix` (`2026-09-04`, 49 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Python-applicatie met een GTK4-gebruikersinterface voor het bevragen van gegevens met Apache Solr en het toepassen van taalkundige POS-sequentiefilters.
> **Architectuur:** De applicatie maakt gebruik van een GTK4/Libadwaita-frontend gekoppeld aan een Apache Solr-zoekbackend via Python. De verwerking wordt ondersteund door YAML-geconfigureerde filters voor het analyseren van POS-sequenties.
- **Talen:** Python (15), YAML (4), Shell/Bash (1)
- **Assets:** .jpg (4), .svg (3), .zip (3)
- **Gedetecteerde stack:** Apache Solr / Lucene, GTK4 / Libadwaita
- **Statische DNA-synthese:** eagle045.py: ========================================================================================= 🔥 PROJECT FENIX (v45) - MATRIX UX, OPERATOR PRESERVER & SAFE RANGES ========================================================================================= ANTI-LITE MANIFEST (DE HEILIGE WETTEN VAN DIT SCRIPT | Symbols: TraceWindow, MatrixWindow, FenixQueryApp, bind_field_value(), generate_help_docs() | Stack: Apache Solr / Lucene, GTK4 / Libadwaita
- **Actieve codebestanden:** `new/eagle045.py, yamls/Béatrice_Daille_minimal_pos_sequence_filter.yaml, yamls/Rutten_Pas_Kleynenberg_pos_sequence_filter.yaml, yamls/EN_Béatrice_Daille_sliding_window_pos_sequence_filter.yaml, yamls/NL_Béatrice_Daille_sliding_window_pos_sequence_filter.yaml, clean/fork/FINAL.py, clean/fork/part3_6.py, clean/fork/part3_5.py`

### `firestore` (`2026-08-18`, 10 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een Flask-gebaseerd dashboard voor het monitoren en visualiseren van energie- en automatiseringsgegevens uit diverse bronnen met behulp van SQLite en Firestore.
> **Architectuur:** De architectuur bestaat uit een Python Flask-backend die gegevens uit een lokale SQLite-database en Firebase Firestore ontsluit via een HTML5-gebruikersinterface. Het systeem is gecentraliseerd rondom Docker en verwerkt telemetriegegevens van onder andere zonne-energie, P1-meters en slimme verlichting.
- **Talen:** Python (2), YAML (1), HTML5 (1)
- **Assets:** .ico (2), .png (2)
- **Gedetecteerde stack:** Docker / Podman, Google Cloud / BigQuery
- **Statische DNA-synthese:** UI Title: 'Peek Matrix 2026 - Energy & Automation Dashboard' | Symbols: get_db_connection(), sanitize_value(), serve_index(), get_status(), get_sqlite_data(), verwerk_tabel() | Stack: Docker / Podman, Google Cloud / BigQuery
- **Actieve codebestanden:** `server_paddel.py, public/index.html, migreer.py, config.yaml`

### `fontfilm` (`2026-09-12`, 6108 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project scant en compileert lettertypebestanden naar een Fontbook-catalogus op basis van YAML-configuraties en een SQLite-database.
> **Architectuur:** De architectuur combineert Python-bibliotheken zoals fontTools, fontforge, reportlab en weasyprint voor de analyse en PDF-generatie van lettertypen. Een SQLite-database fungeert als metadata-opslag voor synchronisatie en integriteitscontroles.
- **Talen:** Python (14), YAML (5)
- **Assets:** .ttf (189), .otf (12), .zip (5), .jpg (2), .png (2), .jpeg (1)
- **Gedetecteerde stack:** Docker / Podman, PDF / Typography Pipeline
- **Statische DNA-synthese:** Scanner_by_Lite.py: Scanner for Fontbook based on YAML configuration and SQLite metadata database. Inclusief automatische database-synchronisatie, robuuste duplicaat-check en permissieherstel. | Symbols: get_time_str(), draw_clock_dial(), parse_font_worker(), process_font_with_timeout(), main(), sanitize_str() | Stack: Docker / Podman, PDF / Typography Pipeline
- **Actieve codebestanden:** `A_lite.py, A.py, fontbook.yaml, metric_trawler.py, Scanner_by_Lite.py, Compiler_by_lite.py, import/make_font_pdf_catalogus.py, import/rescue_PRIMAFONT_fonts.py`
- **Slim gesnoeide submappen:** fonts_lib (high_fanout_no_code (13 subdirs: Adobe, Alfabetisch, Apple, Bitstream, Corrupt, Dalton_Maag, Google, ITC...)); import/Another_Fonts.2 (high_fanout_no_code (13 subdirs: Adobe, Alfabetisch, Apple, Bitstream, Corrupt, Dalton_Maag, Google, ITC...)); import/Another_Fonts.3 (asset_sink (4189 files, 4189 binary/media/font assets)); import/Another_Fonts.1/LinoType (asset_sink (4186 files, 4186 binary/media/font assets)); import/Another_Fonts.1/PrimaFont/Classic-Collection Type1 (high_fanout_no_code (184 subdirs: AME, ANT, ARK, AVA, BAS, BAU, BEG, BEI...))

### `fonthack` (`2026-08-23`, 7 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Het project Fonthack is een initiatief dat zich richt op het bewerken of aanpassen van lettertypes.
> **Architectuur:** Er is geen technische architectuur gedocumenteerd omdat het project geen actieve broncodebestanden of gedetecteerde technologieën bevat. De huidige status is beperkt tot de initiële projectstructuur.
- **Talen:** geen code gedetecteerd
- **Assets:** .ttf (4)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** fonthack

### `gemomni` (`2026-09-06`, 90 bestanden)
> **Domein:** Browser-native AI and WebGPU engines | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een productiviteitstool die Google Gemini integreert in de browse-ervaring via een Android-applicatie en geautomatiseerde deployment-scripts.
> **Architectuur:** De codebase combineert een Kotlin Android-applicatie met een GeminiActivity en WebView, ondersteund door Python-scripts voor geautomatiseerd beheer van Google Play Store-tracks. De deployment-pijplijn maakt gebruik van de Google API Client en Shell-scripts voor build- en releasebeheer.
- **Talen:** Kotlin (4), Python (4), Shell/Bash (3)
- **Assets:** .png (43), .jpg (6), .jpeg (2), .jar (1)
- **Gedetecteerde stack:** Android SDK / WebView, Google Cloud / BigQuery
- **Statische DNA-synthese:** GemOmni GemOmni is a productivity extension for Google Chrome that seamlessly integrates Google Gemini into your browsing experience. Features - **Send Text to Gemini**: Simply select any text on a webpage, right-click, and choose "Send to Gemini" from the context menu to instantly process the text. - **Analyze URLs**: Click the GemOmni extension icon in your toolbar to send the current page's URL to Gemini for summarization or analysis. | Symbols: main(), parse_playstore_md(), list_tracks(), GeminiActivity, val | Stack: Android SDK / WebView, Google Cloud / BigQuery
- **Actieve codebestanden:** `GemOmni/Makefile, GemOmni/upload_to_procuction_track.py, GemOmni/app/build.gradle.kts, GemOmni/upload_store_listing.py, GemOmni/upload_to_test_track.py, GemOmni/check_tracks.py, gclouder.sh, GemOmni/store/resmaker.sh`

### `home_matrix` (`2026-08-09`, 125 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een gecentraliseerd, lokaal smart home-monitoringssysteem dat real-time energieverbruik, zonne-energie, Philips Hue-gebeurtenissen en weerdata verzamelt en visualiseert.
> **Architectuur:** De applicatie maakt gebruik van een Python Flask-webserver en een supervisor-patroon om achtergronddaemons aan te sturen voor data-acquisitie. Gegevens worden opgeslagen in een SQLite-database en het systeem is ontworpen om te draaien in Docker- of Podman-containers.
- **Talen:** Python (45), Shell/Bash (2), HTML5 (1)
- **Assets:** .tar (1), .apk (1)
- **Gedetecteerde stack:** Docker / Podman
- **Statische DNA-synthese:** Home-Matrix & P1 Dashboard Een gecentraliseerd, lokaal smart home-monitoringssysteem op basis van een Python Flask-webserver en een supervisor-patroon dat zelfstandig achtergronddaemons aanstuurt. Het systeem verzamelt en visualiseert real-time energieverbruik (P1), zonne-energie (Growatt), Philips Hue-gebeurtenissen en weerdata (IDELFT55). 1. Architectuur & Componenten Het systeem werkt volgens een supervisor-patroon waarbij de hoofdapplicatie ( | Symbols: test_hue_live_polling(), check_ip(), scan_network(), log_p1_measurement(), fetch_p1_data(), process_mailbox() | Stack: Docker / Podman
- **Actieve codebestanden:** `home_matrix.py, backup6/home_matrix.py, backup6/test_hue.py, backup6/test_growatt_api.py, backup6/scan_netwerk.py, backup6/test_p1.py, backup6/deamon_hue.py, backup6/deamon_weather.py`

### `html` (`2026-04-07`, 69 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een webgebaseerde applicatie genaamd Synaptix Studio die fungeert als een Spartan Neural Network Designer en beschikt over interactieve Sitar audio-engines.
> **Architectuur:** De applicatie is gebouwd met HTML5, JavaScript en CSS3 en maakt gebruik van Web Audio en DSP-technologieën voor realtime geluidsverwerking in de browser. De frontend bestaat uit diverse HTML-interfaces die direct audio-effecten en -synthese aansturen via functies zoals playSound.
- **Talen:** HTML5 (32), JavaScript (4), CSS3 (1)
- **Assets:** .wav (12), .png (9), .ico (1), .zip (1), .apk (1)
- **Gedetecteerde stack:** Web Audio / DSP
- **Statische DNA-synthese:** UI Title: 'Sitar Workbench v33 - Pure Path' | https://fantastic-crostata-2de698.netlify.app/ https://docs.pwabuilder.com/#/builder/android?id=publish | Symbols: playSound | Stack: Web Audio / DSP
- **Actieve codebestanden:** `netlify/Metheny/index.html, netlify/Metheny/index32.html, netlify/Metheny/index30.html, netlify/Metheny/index28.html, netlify/Metheny/index27.html, netlify/Metheny/index26.html, netlify/Metheny/index25.html, netlify/Metheny/index24.html`

### `instagrid` (`2026-10-04`, 10 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project genereert en uploadt Instagram-afbeeldingstegels met behulp van PIL en cairosvg.
> **Architectuur:** Een Python-gebaseerde pipeline die PIL en cairosvg gebruikt voor het renderen en samenstellen van afbeeldingstegels. De scripts build_grid_final.py en upload_tegels.py verzorgen respectievelijk de generatie en de upload van de resulterende media.
- **Talen:** Python (2)
- **Assets:** .png (7), .svg (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: genereer_definitieve_instagram_tegels() | Langs: Python
- **Actieve codebestanden:** `upload_tegels.py, build_grid_final.py`

### `ircopter` (`2026-09-04`, 2 bestanden)
> **Domein:** Low-level OS, flashing and forensics | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Een Python-project genaamd ircopter dat een sniffer-script bevat.
> **Architectuur:** De applicatie is opgebouwd rond een enkel Python-script met een basale main-functie. Er zijn geen aanvullende bibliotheken of frameworks gedetecteerd.
- **Talen:** Python (1)
- **Assets:** .jpg (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: main() | Langs: Python
- **Actieve codebestanden:** `sniff01.py`

### `kobo` (`2026-08-27`, 455 bestanden)
> **Domein:** Low-level OS, flashing and forensics | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een PyQt6-desktopapplicatie voor het beheren van Kobo-apparaten, inclusief apparaatdetectie, bestandsscanning en datamigratie.
> **Architectuur:** De applicatie maakt gebruik van een PyQt6-interface met asynchrone worker-threads voor apparaatdetectie, bestandsscans en migraties, ondersteund door een SQLite-database. Docker en aanvullende Python- en Shell-scripts ondersteunen de deployment en het beheer van afbeeldingen.
- **Talen:** Python (2), Shell/Bash (1)
- **Assets:** .png (19), .jpg (11), .otf (6), .ttf (3)
- **Gedetecteerde stack:** Docker / Podman
- **Statische DNA-synthese:** Symbols: format_size(), main(), DeviceDetectWorker, FileScanWorker, MigrationWorker, KoboManagerApp | Stack: Docker / Podman
- **Actieve codebestanden:** `images/merge_old_to_new.py, images/compare.sh, kobo_manager.py`
- **Slim gesnoeide submappen:** Kobo_Aura_Edition_2_2016/AntiGravity/Calibre Library (high_fanout_no_code (13 subdirs: C.E.S. Arps, Dan Brown, Darwin, Dennis Taylor, Gerard Reve, Hans Rosling, J.K. Rowling, J.R.R. Tolkien...)); Kobo_Aura_Edition_2_2016/Digital Editions/Annotations/Dennis Taylor (empty_dir); Kobo_Aura_Edition_2_2016/Digital Editions/Annotations/Gerard Reve (empty_dir); Kobo_Aura_Edition_2_2016/Digital Editions/Annotations/AntiGravity/Stevens (empty_dir); Kobo_Aura_Edition_2_2016/Digital Editions/Annotations/Calibre Library/J.R.R. Tolkien (empty_dir)

### `logitech` (`2026-08-30`, 3 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project voorkomt dat Logitech-luidsprekers in stand-by gaan door periodiek een onhoorbare toon af te spelen via PipeWire.
> **Architectuur:** Het project maakt gebruik van Bash-scripts om een achtergrondtaak te configureren die via PipeWire een onhoorbare 10Hz-toon genereert. Dit voorkomt dat aangesloten audioapparatuur in de energiebesparende stand-by-modus gaat.
- **Talen:** Shell/Bash (2)
- **Gedetecteerde stack:** PipeWire / Audio DSP
- **Statische DNA-synthese:** Logitech sound keep-alive hack [tomsguide-url]: https://forums.tomsguide.com/threads/prevent-speakers-standby-mode.375550/#post-1650702 Dit project bevat een script dat voorkomt dat Logitech computerluidsprekers automatisch in een energiebesparende stand-by-modus (ErP) springen door op de achtergrond periodiek een onhoorbare 10Hz toon af te spelen via PipeWire. Install ```bash ./install_logitech_keepalive.sh Uninstall ```bash | Stack: PipeWire / Audio DSP
- **Actieve codebestanden:** `README.md, uninstall_logitech_keepalive.sh, install_logitech_keepalive.sh`

### `louter` (`2026-08-26`, 15 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project genereert hoogwaardige profielen en omslagen met behulp van de Python Imaging Library.
> **Architectuur:** Het project is opgebouwd als een Python-script dat de PIL-bibliotheek aanroept voor beeldverwerking en font-manipulatie. De uitvoering is gecentreerd rond specifieke functies voor het laden van lettertypen en het genereren van visuele profielen en omslagen.
- **Talen:** Python (1)
- **Assets:** .png (5), .mp4 (3), .jpg (3), .ttf (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: laad_font(), maak_high_end_profiel(), maak_high_end_omslag() | Langs: Python
- **Actieve codebestanden:** `generate_2026.py`

### `marvin` (`2026-09-05`, 43 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is ontworpen voor de automatische detectie van Grove-sensoren op een embedded Arduino-platform met LoRa-connectiviteit.
> **Architectuur:** De architectuur combineert embedded C++ firmware voor sensoruitlezing via de Adafruit Unified Sensor Driver met Python-scripts voor boarddetectie en procesbeheer. Het systeem is ontworpen voor IoT-telemetrie via LoRa-netwerken.
- **Talen:** Arduino/Embedded C++ (14), C/C++ Header (5), C++ (4), Python (2), Shell/Bash (1)
- **Gedetecteerde stack:** LoRa / IoT
- **Statische DNA-synthese:** Adafruit Unified Sensor Driver # Many small embedded systems exist to collect data from sensors, analyse the data, and either take an appropriate action or send that sensor data to another system for processing. One of the many challenges of embedded systems design is the fact that parts you used today may be out of production tomorrow, or system requirements may change and you may need to choose a different sensor down the road. | Symbols: get_term_size(), add_log(), dashboard_worker(), set_progress(), enqueue_output(), run_in_isolated_process_group_with_queue() | Stack: LoRa / IoT
- **Actieve codebestanden:** `marvin_auto_detect_grove/marvin_auto_detect_grove.ino, 08backup/marvin_auto_detect_grove.ino, 07backup/marvin_auto_detect_grove.ino, 07backup/make.py, make.py, 06backup.still.lying/marvin_auto_detect_grove.ino, 06backup.still.lying/Makefile, 05backup.still.sucks/Makefile`

### `metromoo` (`2026-09-14`, 29 bestanden)
> **Domein:** Cloud-native virtual worlds | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Progressive Web Application die dient als client voor een LambdaMOO-omgeving, ondersteund door een Python-backend.
> **Architectuur:** De architectuur bestaat uit een HTML5 en JavaScript Progressive Web Application met service workers, die verbinding maakt met een Python-gebaseerde backend server. De frontend is ontworpen om standalone of via Cloudflare Pages te worden gehost.
- **Talen:** Python (11), HTML5 (5), JavaScript (4)
- **Gedetecteerde stack:** Docker / Podman
- **Statische DNA-synthese:** UI Title: 'moo.demetro.nl - Standalone PWA' | Stack: Docker / Podman
- **Actieve codebestanden:** `work/websitebuid/metro_pwa/index.html, work/websitebuid/metro_pwa/sw.js, work/websitebuid/metro_pwa/manifest.json, work/websitebuid/makemock.py, work/websitebuid/OLD.mediro_cloudflare_pages/index.html, work/websitebuid/OLD.mediro_cloudflare_pages/sw.js, work/websitebuid/OLD.mediro_cloudflare_pages/manifest.json, work/websitebuid/metrogames_server.py`

### `miband2` (`2026-08-21`, 9 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een Progressive Web App die via Bluetooth Low Energy verbinding maakt met een MiBand 2-wearable om telemetriedata te streamen, hardwarefuncties aan te sturen en apparaatgegevens uit te lezen.
> **Architectuur:** De applicatie is ontworpen als een offline-first Progressive Web App die via de Web Bluetooth API rechtstreeks communiceert met de MiBand 2-hardware. De architectuur maakt gebruik van een service worker voor offline beschikbaarheid en bevat specifieke modules voor data-extractie en hardware-aansturing.
- **Talen:** HTML5 (4), JavaScript (1)
- **Assets:** .ico (1), .jpg (1)
- **Gedetecteerde stack:** Bluetooth Classic / BLE
- **Statische DNA-synthese:** UI Title: 'Gemini MiBand2 Multi-Streamer' | Stack: Bluetooth Classic / BLE
- **Actieve codebestanden:** `bluetooth_pwa/index.html, bluetooth_pwa/tril.html, bluetooth_pwa/larger.html, bluetooth_pwa/small.html, bluetooth_pwa/sw.js, bluetooth_pwa/manifest.json`

### `nautilus` (`2026-10-06`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd nautilus, bevat momenteel geen actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** De technische architectuur kan niet worden vastgesteld door het ontbreken van broncode en gedetecteerde componenten. Het project bevindt zich in een lege of initiële staat.
- **Talen:** geen code gedetecteerd
- **Assets:** .tar (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** nautilus

### `nexus` (`unknown`, 0 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd "nexus", bevat momenteel geen actieve code of gedetecteerde technologieën.
> **Architectuur:** De technische architectuur is onbepaald vanwege het ontbreken van actieve codebestanden en gedetecteerde technologieën in de metadata. Het project bevindt zich in een lege of niet-geïnitialiseerde staat.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** nexus

### `nvidia` (`2026-09-10`, 73 bestanden)
> **Domein:** Cloud-native virtual worlds | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een multi-user 3D Fractal Multiverse Progressive Web App (PWA) die wordt aangedreven door een Python aiohttp-server en beschikt over WebGL- en audio-integratie.
> **Architectuur:** De applicatie combineert een Python aiohttp-backend voor websockets en statische bestandsservering met een frontend PWA die gebruikmaakt van WebGL en Web Audio DSP. Daarnaast bevat het systeem een PyQt6-gebaseerde desktop overlay en systeemmonitoringfuncties voor hardware-telemetrie.
- **Talen:** Python (15), HTML5 (8), C (7), JavaScript (4), YAML (2)
- **Assets:** .png (9), .svg (4), .mp4 (3), .mov (1)
- **Gedetecteerde stack:** Docker / Podman, Web Audio / DSP, WebGL
- **Statische DNA-synthese:** UI Title: '3D Fractal Multiverse PWA' | fractal_server.py: Multi-user Fractal Multiverse PWA Draait via Python aiohttp op poort 31415. Bevat: Toast tekstballon notificatie voor Share, Ingangspunt URL behoud, Semi-transparante HUD, Universe-specifieke Warp Home, SVG Infinity Favicon (/favicon.svg), Vloeiende demping en Default Connected mode. | Symbols: handle_index(), websocket_handler(), serve_static_root_files(), init_app(), DesktopMonitorOverlay, get_running_pids() | Stack: Docker / Podman, Web Audio / DSP, WebGL
- **Actieve codebestanden:** `kleynenberg-hrd/Makefile, googledrive/Makefile, kleynenberg-hrd/main.py, kleynenberg-hrd/Dockerfile, kleynenberg-hrd/index.html, kleynenberg-hrd/app.yaml, kleynenberg-hrd/sw.js, kleynenberg-hrd/manifest.json`

### `nxt` (`2026-09-04`, 527 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project maakt verbinding met LEGO Mindstorms NXT-stenen en sensoren om deze aan te sturen en uit te lezen via een Python-interface.
> **Architectuur:** De architectuur is opgebouwd rond de nxt-python bibliotheek voor hardware-interactie via Bluetooth of USB, gecombineerd met een GUI en een PDF-rapportagecomponent. Het systeem ondersteunt diverse sensoren en motoren via specifieke hardware-protocollen en opcodes.
- **Talen:** Python (443), JavaScript (1)
- **Assets:** .tar (1), .jpg (1)
- **Gedetecteerde stack:** Bluetooth Classic / BLE, PDF / Typography Pipeline
- **Statische DNA-synthese:** generic.py: The :mod:`nxt.sensor.generic` module supports the sensors manufactured by LEGO. | Symbols: create_documentation_pdf(), NXTControllerApp, log(), run_probe(), test_connection(), Opcode | Stack: Bluetooth Classic / BLE, PDF / Typography Pipeline
- **Actieve codebestanden:** `nxt_app_swapper/generate_pdf.py, nxt_gui.py, test_licht.py, nxt_test_drukker.py, nxt_probe.py, v1_nxt_gui.py, test_find.py, test_nxt.py`
- **Slim gesnoeide submappen:** nxt_env/include (empty_dir); nxt_env/lib/python3.14/site-packages/pip-26.2.1.dist-info/licenses/src/pip/_vendor (high_fanout_no_code (18 subdirs: cachecontrol, certifi, distlib, distro, idna, msgpack, packaging, pkg_resources...))

### `ollama` (`unknown`, 0 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project betreft de initialisatie of configuratie van Ollama, maar bevat momenteel geen actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Vanwege het ontbreken van actieve bronbestanden en gedetecteerde technologieën is er geen specifieke technische architectuur gedefinieerd. Het project bevindt zich in een lege of niet-geconfigureerde staat.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** ollama

### `osint` (`2026-08-28`, 7 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit Python-project stabiliseert en verzacht beeldsignalen of videoframes met behulp van OpenCV en NumPy.
> **Architectuur:** De applicatie maakt gebruik van OpenCV en NumPy om beeldbewerking en signaalstabilisatie uit te voeren. Via functies voor voortschrijdende gemiddelden en smoothing worden frames of datapunten vloeiender gemaakt.
- **Talen:** Python (1)
- **Assets:** .mp4 (5), .wav (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: moving_average(), smooth() | Langs: Python
- **Actieve codebestanden:** `flash_stabiel.py`

### `pdfguru` (`2026-08-27`, 20 bestanden)
> **Domein:** Publishing and typographic pipelines | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project genereert een gedetailleerd frauderapport in PDF-formaat ten behoeve van de ICS Risk/Fraud-afdeling en wetshandhaving.
> **Architectuur:** Het project maakt gebruik van Python en de ReportLab-bibliotheek om programmatisch PDF-documenten te genereren. De architectuur is ontworpen om gestructureerde gegevens, zoals chronologische tijdlijnen en afbeeldingen, samen te voegen in een rapport.
- **Talen:** Python (1)
- **Assets:** .jpg (2), .png (1)
- **Gedetecteerde stack:** PDF / Typography Pipeline
- **Statische DNA-synthese:** disfunctional_make_report.py: Generate an exhaustive, professional English fraud analysis report (PDF) for ICS Risk/Fraud Department and Law Enforcement regarding PDF Guru / LOPOFIST LIMITED, including full company details, the complete chronolocial EVID timeline, and embedded screenshots. | Symbols: build_pdf() | Stack: PDF / Typography Pipeline
- **Actieve codebestanden:** `disfunctional_make_report.py`

### `peek` (`2026-08-31`, 33 bestanden)
> **Domein:** Audio DSP, edge-AI and telemetry | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een live monitoringdashboard dat energieverbruik, gasverbruik, weersgegevens en diverse IoT- en Bluetooth-sensoren visualiseert.
> **Architectuur:** De architectuur bestaat uit een Python-backend die sensorgegevens van Bluetooth, LoRa en slimme meters verzamelt en opslaat in Google Cloud BigQuery. De frontend is een HTML5-gebaseerd live dashboard dat deze telemetriegegevens visualiseert in een matrix-cockpit.
- **Talen:** Python (9), HTML5 (7), Shell/Bash (2), Google Apps Script (1), YAML (1)
- **Assets:** .jpg (3), .png (3), .ico (1)
- **Gedetecteerde stack:** Bluetooth Classic / BLE, Google Cloud / BigQuery, LoRa / IoT
- **Statische DNA-synthese:** UI Title: '[PEEK MONITOR] // Live Matrix Cockpit' | Symbols: NXTControllerApp, log() | Stack: Bluetooth Classic / BLE, Google Cloud / BigQuery, LoRa / IoT
- **Actieve codebestanden:** `server_LG.py, public/index.html, 06backup/index.html, 06backup/server_LG.py, SCRIPT TTN Marvin Lora.gs, config.yaml, 05backup/index.html, 05backup/server_LG.py`

### `polar` (`2026-08-20`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** [API fout: The read operation timed out]
- **Talen:** Python (2)
- **Gedetecteerde stack:** Bluetooth Classic / BLE
- **Statische DNA-synthese:** Symbols: BLEWorker, PolarGUI, hr_data_handler(), read_device_info(), connect_and_listen() | Stack: Bluetooth Classic / BLE
- **Actieve codebestanden:** `polar_gui.py, polar_reader.py`

### `sammy` (`2026-08-01`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd sammy, is een lege repository zonder actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Er is geen softwarearchitectuur of actieve broncode aanwezig in dit project. Er zijn geen programmeertalen of specifieke technologieën gedetecteerd.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** sammy

### `sat` (`2026-09-28`, 11 bestanden)
> **Domein:** Cloud-native virtual worlds | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project is een webgebaseerde Augmented Reality tracker die camera- en sensorgegevens gebruikt om astronomische coördinaten in 3D te visualiseren.
> **Architectuur:** De frontend is een webapplicatie met service worker-ondersteuning die apparaatsensoren en camera-inputs combineert met astronomische berekeningen voor 3D-visualisatie. De backend maakt gebruik van een Python-socketserver voor netwerkcommunicatie.
- **Talen:** JavaScript (3), Python (1), HTML5 (1), Shell/Bash (1), CSS3 (1)
- **Assets:** .png (2), .svg (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** UI Title: 'Gemini SAT - AR Tracker' | Symbols: initCamera, eulerToQuaternion, multiplyQuat, getScreenQuat, slerp, initSensors | Langs: JavaScript, Python, HTML5, Shell/Bash
- **Actieve codebestanden:** `app.js, index.html, manifest.json, sw.js, astro.js, style.css, py.sh, genesis.py`

### `skyrex` (`2026-09-05`, 2 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project documenteert een verzameling links naar mobiele applicaties in de Google Play Store voor het besturen van drones.
> **Architectuur:** De repository bevat geen actieve broncode en bestaat uitsluitend uit een README-bestand met externe links. Er is geen software-architectuur aanwezig.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Apps https://play.google.com/store/apps/details?id=com.cooingdv.kyufo&pcampaignid=web_share https://play.google.com/store/apps/details?id=com.lewei.jyufo&pcampaignid=web_share https://play.google.com/store/apps/details?id=com.lewei.jyufo&pcampaignid=web_share https://play.google.com/store/apps/details?id=com.cooingdv.kyfpv&pcampaignid=web_share https://play.google.com/store/apps/details?id=com.yls.skydrone&pcampaignid=web_share
- **Actieve codebestanden:** `README.md`

### `solr` (`2026-09-02`, 1489 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Dit project omvat een automatisch gegenereerde JavaScript-client SDK voor de Apache Solr v2 API en bijbehorende webinterface-componenten voor het beheren en bevragen van zoekindexen.
> **Architectuur:** De frontend maakt gebruik van AngularJS, D3.js en jQuery om een beheerinterface te bieden voor Solr-schema's en queries, terwijl de API-interactie verloopt via een OpenAPI-gegenereerde JavaScript SDK. Ondersteunende Python-scripts faciliteren aanvullende dataverwerking en API-aanroepen.
- **Talen:** JavaScript (49), CSS3 (35), HTML5 (32), Python (7), Shell/Bash (5)
- **Assets:** .png (93), .jar (14), .svg (5), .gif (4), .ico (1)
- **Gedetecteerde stack:** Apache Solr / Lucene
- **Statische DNA-synthese:** v2_api V2Api - JavaScript client for v2_api OpenAPI spec for Solr's v2 API endpoints This SDK is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project: - API version: 10.0.0 - Package version: 10.0.0 - Generator version: 7.14.0 - Build package: org.openapitools.codegen.languages.JavascriptClientCodegen Installation For [Node.js](https://nodejs.org/) npm To publish the library as a [npm](https://www.npmjs.com/) | Symbols: d3_class, d3_arrayCopy, d3_arraySlice, d3_Map, d3_this, d3_rebind | Stack: Apache Solr / Lucene
- **Actieve codebestanden:** `complex.py, 50_xml.py, 50.py, example.api.py, apache/solr-10.0.0-slim/server/solr-webapp/webapp/ui/composeApp.js, apache/solr-10.0.0-slim/server/solr-webapp/webapp/libs/solr/index.js, apache/solr-10.0.0-slim/server/solr-webapp/webapp/libs/ui-grid.min.js, apache/solr-10.0.0-slim/server/solr-webapp/webapp/libs/d3.js`
- **Slim gesnoeide submappen:** apache/solr-10.0.0-slim/server/lib/ext (asset_sink (17 files, 17 binary/media/font assets)); apache/solr-10.0.0-slim/server/solr-webapp/webapp/WEB-INF/lib (asset_sink (115 files, 115 binary/media/font assets)); apache/solr-10.0.0-slim/server/solr-webapp/webapp/img/ico (asset_sink (126 files, 126 binary/media/font assets)); apache/solr-10.0.0-slim/server/solr-webapp/webapp/ui/composeResources/com.arkivanov.decompose.extensions_compose.generated.resources (empty_dir); apache/solr-10.0.0-slim/server/solr-webapp/webapp/ui/composeResources/components.resources.library.generated.resources (empty_dir)

### `stanford` (`2026-09-04`, 28 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** JA (Geschikt voor R&D-portaal)
> **Onderwerp:** Een high-performance Apache-WSGI NLP-pijplijn met de Stanford POS Tagger die webserverrestricties omzeilt via systeemservice-isolatie.
> **Architectuur:** De architectuur maakt gebruik van een Apache-WSGI-pijplijn voor NLP-extractie, waarbij systeem-level service-isolatie wordt ingezet om restricties zoals SELinux of systemd-sandboxing te omzeilen. De implementatie omvat Python-scripts voor de WSGI-pijplijn en ondersteunende PHP- en JavaScript-componenten voor data-ingestie en -verwerking.
- **Talen:** Python (5), PHP (3), JavaScript (1), Google Apps Script (1)
- **Assets:** .png (3), .svg (1)
- **Gedetecteerde stack:** Google Cloud / BigQuery
- **Statische DNA-synthese:** High-Performance Apache-WSGI NLP Pipeline with Stanford POS Tagger An enterprise-grade, blazing-fast NLP extraction pipeline designed to overcome strict web server permissions (such as SELinux or systemd sandboxing in Apache) and maximize performance through system-level service isolation. Co-authored & engineered by Steve (HP Server Architect) & AI Assistant. 🚀 The Architecture Challenge & Breakthrough The Problem Web applications running under  | Symbols: helloPOSTERMPLURAL | Stack: Google Cloud / BigQuery
- **Actieve codebestanden:** `example_from_nodejs.js, Makefile, stanford_wsgi_pipeline_VERBOSE.py, stanford_wsgi_pipeline.py, README.md, history/phoenix/make_strict_phoenix.py, README_HTTPS_Fedora_kleynenberg_net.pdf, history/patent_ingestor/php/convert_text_to_json_query.php`

### `suno` (`2026-08-25`, 20 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd suno, bevat op basis van de metadata geen actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Er is geen technische architectuur beschikbaar omdat het project geen actieve broncode of gedetecteerde componenten bevat. Het project bevindt zich in een lege of initiële staat.
- **Talen:** geen code gedetecteerd
- **Assets:** .jpg (4), .mp4 (3), .png (3), .mp3 (3), .jpeg (1)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** suno

### `taks` (`2026-10-06`, 254 bestanden)
> **Domein:** Enterprise intelligence and fiscal AI | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project indexeert en presenteert de Nederlandse Taxonomie (NT21) XML-schema's en entrypoints voor de inkomstenbelastingaangifte van 2026.
> **Architectuur:** De architectuur is opgebouwd uit statische HTML5-indexbestanden die dienen als navigatie- en presentatielaag voor de lokale XML-taxonomiestructuur. Het project bevat mappen voor validatie, presentatie en entrypoints van de Belastingdienst-aangifte.
- **Talen:** HTML5 (5)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** UI Title: 'Index of /nt21/bd/20261209.b/validation' | https://www.nltaxonomie.nl/nt21/bd/20261209.b/entrypoints/bd-rpt-ihz-aangifte-2026.xsd | Langs: HTML5
- **Actieve codebestanden:** `README.md, taxonomie/nt21/bd/20261209.b/validation/index.html, taxonomie/nt21/bd/20261209.b/presentation/index.html, taxonomie/nt21/bd/20261209.b/entrypoints/index.html, taxonomie/nt21/bd/20261209.b/dictionary/index.html, taxonomie/nt21/bd/20261209.b/index.html`

### `totem` (`2026-08-13`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project, genaamd totem, bevat momenteel geen actieve codebestanden of gedetecteerde functionaliteit.
> **Architectuur:** De technische architectuur is niet gedefinieerd vanwege het ontbreken van broncode en gedetecteerde technologieën. Het project bevindt zich in een lege of niet-geïmplementeerde staat.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** totem

### `vodafone` (`2026-10-02`, 1 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project is een lege repository of placeholder genaamd vodafone zonder actieve codebestanden of gedetecteerde technologieën.
> **Architectuur:** Er is geen technische architectuur of actieve code aanwezig in deze repository. Het project bevat momenteel geen gedetecteerde technologieën of programmabestanden.
- **Talen:** geen code gedetecteerd
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** vodafone

### `youtube` (`2026-09-07`, 8 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** Dit project haalt YouTube-video- en muziekplaylists op, schoont de titels op en clustert de resultaten.
> **Architectuur:** Het project bestaat uit Python-scripts die YouTube-playlistgegevens ophalen en verwerken. De data wordt opgeschoond en vervolgens geanalyseerd met behulp van pandas en scikit-learn voor clustering.
- **Talen:** Python (4)
- **Gedetecteerde stack:** -
- **Statische DNA-synthese:** Symbols: clean_title(), main() | Langs: Python
- **Actieve codebestanden:** `music/02_cluster_results.py, video/02_cluster_results.py, video/01_get_youtube_video_playlists.py, music/01_get_youtube_music_playlists.py`

### `zephyr` (`2026-08-20`, 42 bestanden)
> **Domein:** Internal utility / maintenance | **Publiek portaal:** NEE (Intern / utility)
> **Onderwerp:** [API fout: The read operation timed out]
- **Talen:** Python (4), Java (4), Shell/Bash (1)
- **Assets:** .png (15), .jar (3), .tar (1), .apk (1), .dex (1)
- **Gedetecteerde stack:** Android SDK / WebView, Bluetooth Classic / BLE, GTK4 / Libadwaita
- **Statische DNA-synthese:** Android: com.NewApp | zephyr_gui.py: Zephyr CardioVision - Native GNOME ECG & Telemetry Patient Monitor Built with GTK 4, Libadwaita, and Cairo. Usage: python3 zephyr_gui.py --demo python3 zephyr_gui.py --mac C8:3E:99:0D:9A:67 | Symbols: SyntheticEcgGenerator, EcgCanvas, EcgFilter, TelemetryPanel, MainWindow, CardioVisionApp | Stack: Android SDK / WebView, Bluetooth Classic / BLE, GTK4 / Libadwaita
- **Actieve codebestanden:** `zephyr_gui.py, keep/zephyr_gui.py, tryme.sh, zephyr_bioharness.py, zephyr.py, spieken/src/com/NewApp/NewConnectedListener.java, spieken/bin/AndroidManifest.xml, spieken/gen/com/NewApp/BuildConfig.java`
- **Slim gesnoeide submappen:** spieken/assets (empty_dir); spieken/bin/classes/com/NewApp (asset_sink (17 files, 17 binary/media/font assets))
