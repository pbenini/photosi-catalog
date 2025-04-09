# Photosì Catalog Site Builder

Generatore di sito web statico per la documentazione delle relazioni tra servizi Photosì.

Le SPECIFICHE del builder sono in specifiche/Readme.MD

## Descrizione

Questo progetto genera un portale web statico per consultare la documentazione delle relazioni tra servizi di Photosì. Il portale visualizza le interazioni tra servizi attraverso eventi, in forma di grafici interattivi.

## Installazione

```bash
# Creazione dell'ambiente virtuale
python -m venv venv

# Attivazione dell'ambiente virtuale
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# Installazione delle dipendenze
pip install -r requirements.txt
```

## Utilizzo

```bash
python src/main.py --input /path/to/asyncapi-files --output /path/to/output
```

Per verificare l'output generato è possibile eseguire il seguente comando
```bash
cd /path/to/output && python -m http.server 8000
```
Quindi aprire il browser all'indirizzo http://localhost:8000

## Struttura del progetto

```
photosi-catalog-site-builder/
├── README.md                   # Documentazione del progetto
├── requirements.txt            # Dipendenze Python
├── src/                        # Codice sorgente
│   ├── __init__.py
│   ├── main.py                 # Punto di ingresso dell'applicazione
│   ├── parser/                 # Elaborazione dei file YAML
│   │   ├── __init__.py
│   │   ├── service_parser.py   # Parsing dei file di servizio
│   │   ├── event_parser.py     # Parsing dei file di eventi
│   │   └── channel_parser.py   # Parsing dei file di canali
│   ├── models/                 # Modelli di dati
│   │   ├── __init__.py
│   │   ├── service.py          # Classe per i servizi
│   │   ├── event.py            # Classe per gli eventi
│   │   └── channel.py          # Classe per i canali
│   ├── generators/             # Generazione dei file statici
│   │   ├── __init__.py
│   │   ├── site_generator.py   # Generatore del sito completo
│   │   ├── service_page.py     # Generatore delle pagine dei servizi
│   │   └── event_page.py       # Generatore delle pagine degli eventi
│   ├── utils/                  # Funzioni di utilità
│   │   ├── __init__.py
│   │   ├── graph_utils.py      # Utility per generare grafici di relazioni
│   │   └── file_utils.py       # Utility per la gestione dei file
│   └── templates/              # Template HTML
│       ├── base.html           # Template base
│       ├── service_page.html   # Template per la pagina del servizio
│       └── event_page.html     # Template per la pagina dell'evento
├── static/                     # File statici (CSS, JS)
│   ├── css/
│   │   └── style.css           # Stile del sito
│   ├── js/
│   │   └── main.js             # JavaScript per la navigazione e interazioni
│   └── images/                 # Immagini e icone
├── output/                     # Output generato
│   ├── index.html              # Pagina principale
│   ├── services/               # Pagine dei servizi
│   └── events/                 # Pagine degli eventi
└── tests/                      # Test unitari
    ├── __init__.py
    ├── test_parser.py
    └── test_generator.py
```

## Tecnologie

- Python: Generazione del sito
- Jinja2: Template HTML
- React Flow: Visualizzazione interattiva dei grafici
- dagre: Layout del grafico
