# Restraunt-banks

MVP backend for matching restaurant surplus donations to the nearest nonprofit with pickup window optimization.

## Prerequisites
- Python 3.10+
- Git

## Setup
```bash
# Clone
git clone https://github.com/kitili/Restraunt-banks.git
cd Restraunt-banks

# Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize the SQLite database (creates tables)
python3 - << "PY"
from backend.app.db.init_db import *
print("DB initialized")
PY

# Run the dev server
./run.sh
# or
# uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:
```bash
curl http://localhost:8000/health
```

## UI
Visit http://localhost:8000/ui to register nonprofits and post donations.

## API

### Register a nonprofit
```bash
curl -X POST http://localhost:8000/nonprofits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Food Bank",
    "address": "123 Hope St, Nairobi",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "contact_phone": "+254700000000",
    "contact_email": "contact@cityfb.org",
    "pickup_windows": [
      {"start_time": "09:00", "end_time": "12:00"},
      {"start_time": "14:00", "end_time": "18:00"}
    ]
  }'
```

### Post a donation (auto-match)
Use ISO 8601 timestamps for `ready_at` and `expires_at`.
```bash
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
IN1H=$(date -u -d "+1 hour" +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST http://localhost:8000/donations \
  -H "Content-Type: application/json" \
  -d "{
    \"donor_name\": \"Good Bites Restaurant\",
    \"address\": \"456 Market Rd\",
    \"latitude\": -1.2900,
    \"longitude\": 36.8200,
    \"ready_at\": \"$NOW\",
    \"expires_at\": \"$IN1H\",
    \"food_description\": \"10 boxed meals\"
  }"
```
Response includes the donation and, if matched, the `match` with `distance_km` and `pickup_eta`.

### Confirm pickup
```bash
curl -X POST http://localhost:8000/donations/1/picked-up
```

### Get donation status
```bash
curl http://localhost:8000/donations/1
```

## Production

### Environment Variables
- `FSM_DATABASE_URL`: Database URL (default: SQLite)
- `FSM_CORS_ORIGINS`: Comma-separated allowed origins (default: "*")
- `FSM_DEBUG`: Enable debug mode (default: false)
- `FSM_EXPIRY_INTERVAL_SECONDS`: Background expiry check interval (default: 60)

### PostgreSQL
```bash
export FSM_DATABASE_URL="postgresql://user:pass@localhost/food_matcher"
python3 -c "from backend.app.db.init_db import *; print(DB
