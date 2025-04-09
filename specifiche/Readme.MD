# Documentazione Photosì
Devo generare un portale web per consultare la documentazione delle relazioni tra servizi di Photosì

## Concetti chiave

I concetti attorno ai quali ruota tutta la documentazione sono: Servizi, Eventi e Channel

I **Servizi** sono programmi che eseguono i workflow aziendali. Prendono un input e generano un output. Ogni servizio è corredato di una lista degli eventi, di ogni evento viene specificato se lo riceve e se lo pubblica


Gli **Eventi** sono il modo in cui i servizi interagiscono tra loro per scambiarsi payload.
Gli eventi sono di 3 tipi:
1) Message: Si definiscono tramite Topic e sono comunicazioni asincrone (PubSub)
2) Request: Si definiscono tramite Topic e sono comunicazioni sincrone, ad ogni Request inviata ci si aspetta una Reply (RPC)
3) Command: Sono operazioni schedulate

**Importante**: I nomi dei messaggi devono essere presi dal campo "title" dell'evento anziché dal campo "id". Ad esempio, se un messaggio ha "title: ErpDirectory:BcCustomersUpdated", questo è il nome che deve essere visualizzato nella UI.

## Pagine del sito
Mi aspetto che ci siano questi tipi di pagine:
- pagine di documentazione
- pagine di navigazione

### Pagine di documentazione
Le pagine di documentazione sono di due tipi:
- pagina del servizio
- pagina dell'evento

#### La pagina del **servizio** deve essere come PagServizio.png
**punti chiave della pagina del servizio:**
- Barra verticale a sinistra che permette di navigare sul sito
- barra verticale a sinistra con l'elenco dei link a tutte le pagine dei servizi sul catalogo
- titolo grande con nome del servizio
- campo con breve descrizione in cui ho inserito il link al repo git
- spazio centrale con grafico di relazioni eventi in entrata -> servizio -> eventi in uscita (utilizzeremo React Flow con dagre per il layout del grafico, come nell'esempio visualizzato su https://event-catalog.photosi.online/)
- barra a destra con box con link ai messaggi in entrata e box con link ai messaggi in uscita
- stesso stile css della pagina di esempio che ti ho passato

#### La pagina dell'evento

per ora crea una pagina statica con dentro hello word a cui far puntare tutti i link di eventi in entrata e uscita

## Documentazione in input
La documentazione in input viene passata come percorso a di una cartella la cartella sarà strutturata così:

documentazione/
├─ channels/
├─ messages/
│  ├─ command/
│  ├─ message/
│  │  ├─ aeguideservice/
│  │  │  ├─ message.configurationduplicated.mattedprintsstand.yaml
│  ├─ request/
│  │  ├─ aeguideservice/
│  │  │  ├─ request.accessoryinfo.yaml
├─ services/
   ├─ ae-guide-service.yaml
   ├─ erp-crm-service.yaml

## Tecnologia per i grafici
Per la visualizzazione delle relazioni tra servizi ed eventi utilizzeremo:
- **React Flow**: Framework per creare diagrammi interattivi di nodi e connessioni
- **dagre**: Libreria per il layout automatico dei grafi direzionati
- Integrazione lato client con esportazione di dati JSON da Python

Queste librerie ci permetteranno di creare grafici interattivi simili a quelli presenti nell'esempio visualizzato su https://event-catalog.photosi.online/.

## Considerazioni generali
L'implementazione deve attenersi rigorosamente a questi principi

- La generazione del sito di file statici deve essere fatto in python
- se ti serve fare delle prove e installare moduli fallo dentro un venv
- Codice strutturato e ben organizzato
- Deve essere suddiviso in funzioni ben leggibili
- Deve utilizzare pochi template che verranno poi renderizzati in html con tutti i dati di ogni pagina
- puoi lavorare in questa folder
- non implementare funzionalità su casi d'uso ipotetici
- il catalogo è in sola lettura, ci saranno dei link per navigare tra le pagine ma NESSUN FORM per inserire nuovi messaggi/servizi o modifica di quello che c'è
- *Non inventare e non cercare di indovinare*: stiamo parlando di un portale di generazione del catalogo partendo dalla documentazione che ricevi in input, tutte le informazioni rappresentate devono essere lette dalla documentazione in input, se non trovi qualcosa dimmelo

Voglio cambiare la generazione della documentazione dei servizi:
il comportamento di default è di creare la pagina di documentazione di ogni servizio che trovi nella cartella services.
se ti passo l'arg --service con il nome di un servizio, mi generi solo quella

Creazione dell'indice dei servizi:
Voglio creare un div contenente l'elenco dei link a tutte le pagine dei servizi che hai generato, questo div deve elencare i link incolonnati. Fai riferimento a "indice-servizi.png"
Voglio che modifichi il template della pagina del servizio in modo che includa questo div, così come te l'ho mostrato, voglio che sia dentro l'elemento "sidebar-nav" sotto "Events"

Modifica visualizzazione eventi:
Nel template della pagina del servizio voglio che modifichi l'elemento "event-sidebar".
Va diviso in 2 elementi: received-event-sidebar e sent-event-sidebar.
sent-event-sidebar lo posizioni a destra di service-graph
received-event-sidebar lo posizioni a sinistra di service-graph