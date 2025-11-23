# StablePay

An app that helps people in hyperinflation economies manage stablecoin assets by finding the cheapest conversion rates from local currency and providing financial intelligence on wealth management.

## Installation

1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:

```bash
poetry install
```

3. Set up environment variables (copy `.env.example` to `.env` and fill in your values):

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
BITSO_API_KEY=your_api_key
BITSO_API_SECRET=your_api_secret
BITSO_BASE_URL=https://stage.bitso.com
```

## Running the Application

### Option 1: Using Poetry Shell (Recommended)

Activate the Poetry shell:

```bash
poetry shell
```

Then run:

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

### Option 2: Using Poetry Run

```bash
poetry run python run.py
```

Or:

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Code Formatting

Format code with black and isort:

```bash
poetry run black app/ run.py
poetry run isort app/ run.py
```

## API Endpoints

### POST `/convert`

Convert currency using exchange rates.

**Request:**

```json
{
    "from_ccy": "USD",
    "to_ccy": "BTC",
    "amount": 1000.0
}
```

**Response:**

```json
{
    "converted_amount": 0.0234
}
```

### POST `/cost`

Get the cost (fee) for converting from one currency to another.

**Request:**

```json
{
    "from_currency": "USDC",
    "to_currency": "ARS",
    "amount": 1000.0
}
```

**Response:**

```json
{
    "cost": 6.5,
    "exchange": "bitso"
}
```

### POST `/dijkstra`

Run Dijkstra's algorithm to find shortest path costs from a starting currency.

**Request:**

```json
{
    "start_currency": "USDC",
    "amount": 1000.0
}
```

**Response:**

```json
{
  "costs": {
    "USDC": 0.0,
    "ARS": 0.0065,
    "MXN": 0.0065,
    ...
  },
  "previous": {
    "USDC": null,
    "ARS": "USDC",
    ...
  }
}
```
