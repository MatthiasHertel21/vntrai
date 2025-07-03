# V036 Data Migration

Dieses Verzeichnis enthält Scripts für die Migration der Daten von v036 nach vntrai.

## Migration durchführen

### Option 1: Docker Exec (empfohlen)
```bash
sudo docker-compose exec web python3 migration/migrate_v036_data.py
```

### Option 2: Docker
```bash
./migration/migrate_docker.sh
```

## Was wird migriert?

### Integrations
- **Quelle**: `v036/data/integrations.json`
- **Ziel**: `data/integrations/{uuid}.json` (eine Datei pro Integration)
- **Änderungen**: 
  - `options`-Feld wird entfernt
  - UUID wird generiert falls nicht vorhanden
  - Metadata wird hinzugefügt

### Tools
- **Quelle**: `v036/data/tools.json`
- **Ziel**: `data/tools/{uuid}.json` (eine Datei pro Tool)
- **Änderungen**:
  - UUID wird generiert falls nicht vorhanden
  - Metadata wird hinzugefügt

### Icons
- **Quelle**: `v036/app/static/icons/vendors/`
- **Ziel**: `app/static/icons/vendors/`
- **Änderungen**: Dateien werden kopiert

## Migration Log

Nach der Migration wird ein detailliertes Log in `migration/migration_log.json` erstellt mit:
- Anzahl migrierter Items
- Fehlgeschlagene Migrationen
- Timestamp der Migration

## Rollback

Um die Migration rückgängig zu machen:
```bash
rm -rf data/integrations/*
rm -rf data/tools/*
rm -rf app/static/icons/vendors/*
rm migration/migration_log.json
```

## Troubleshooting

### Python3 nicht gefunden
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3

# CentOS/RHEL
sudo yum install python3
```

### Docker nicht verfügbar
```bash
# Ubuntu/Debian
sudo apt install docker.io
sudo systemctl start docker

# CentOS/RHEL
sudo yum install docker
sudo systemctl start docker
```
