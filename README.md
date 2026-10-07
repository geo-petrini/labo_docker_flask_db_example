# Stack Flask + MariaDB — CRUD

Template minimale per avviare un'applicazione **Flask** (Python 3.12) con un database **MariaDB**, e una piccola CRUD su una risorsa `items`.

## Struttura

```
flask/
├── README.md
├── docker-compose.yml   # servizi app + db
├── Dockerfile           # immagine Python + Flask
├── app.py               # route web e API
├── db.py                # connessione PyMySQL + creazione tabella iniziale
├── requirements.txt     # flask, pymysql
└── templates/
    └── index.html       # pagina HTML che usa l'API via JS
```

## docker-compose.yml

```yaml
services:
  app:
    build: .
    container_name: flask-mariadb-app
    ports:
      - "5010:5000"
    environment:
      DB_HOST: db
      DB_PORT: 3306
      DB_NAME: esempio
      DB_USER: root
      DB_PASS: segreta
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mariadb:11
    container_name: flask-mariadb-db
    ports:
      - "3308:3306"
    environment:
      MARIADB_ROOT_PASSWORD: segreta
      MARIADB_DATABASE: esempio
    volumes:
      - mariadb-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  mariadb-data:
```

## Concetti toccati

- **Build** — `build: .` esegue il `Dockerfile` che installa Flask e PyMySQL.
- **Port mapping** — `"5010:5000"` espone Flask sull'host; `"3308:3306"` espone MariaDB.
- **Variabili d'ambiente** — le credenziali del DB vengono lette da `db.py` con `os.environ.get(...)`.
- **Volume nominato** — `mariadb-data` per la persistenza dei dati.
- **Healthcheck** — l'app parte quando MariaDB è pronto.

## API CRUD (items)

| Metodo | Endpoint | Descrizione |
|---|---|---|
| `GET` | `/api/items` | Lista |
| `POST` | `/api/items` | Crea (`{"title", "note"}`) |
| `GET` | `/api/items/:id` | Singolo |
| `PUT` | `/api/items/:id` | Modifica (`{"title", "note"}`) |
| `DELETE` | `/api/items/:id` | Elimina |

Al primo avvio la tabella `items` viene creata automaticamente e popolata con un elemento di esempio.

## Comandi

```bash
# avviare (compila l'immagine la prima volta)
docker compose up --build

# aprire l'interfaccia web
# http://localhost:5010

# esempi con curl
curl http://localhost:5010/api/items
curl -X POST -H "Content-Type: application/json" -d '{"title":"Ciao","note":"da curl"}' http://localhost:5010/api/items
curl http://localhost:5010/api/items/1
curl -X PUT -H "Content-Type: application/json" -d '{"title":"Aggiornato","note":"ok"}' http://localhost:5010/api/items/1
curl -X DELETE http://localhost:5010/api/items/1

# stato e log
docker compose ps
docker compose logs -f

# fermare tutto
docker compose down

# fermare ed eliminare anche i volumi (perde i dati)
docker compose down -v
```