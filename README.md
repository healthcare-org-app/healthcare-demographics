# demographics-service

demographics-service — domain: patients

- **Port:** 8101
- **Language:** Python 3.11 + Flask
- **Database:** `patients` (Postgres, table `demographics`)
- **Event bus:** Kafka

## API

| Method    | Path                       |
|-----------|----------------------------|
| GET       | `/api/demographics/`          |
| POST      | `/api/demographics/`          |
| GET       | `/api/demographics/<id>`      |
| PUT/PATCH | `/api/demographics/<id>`      |
| DELETE    | `/api/demographics/<id>`      |
| GET       | `/health`                  |
| GET       | `/ready`                   |

## Events

**Publishes:** (none)
**Subscribes:** patient.updated

## HTTP peer dependencies

- `patients-service`
- `audit-log-service`

## Local dev

```bash
pip install -e ../../libs/py-healthcare-common
pip install -r requirements.txt
cp .env.example .env
(cd ../../infra && docker compose up -d postgres kafka kafka-init)
python -m app.main
```

## Tests

```bash
pytest
```
