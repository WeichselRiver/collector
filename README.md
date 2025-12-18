# collector
Helpful Tools for stamp collectors

## Features

### DuckDB Storage Script (`collector_db.py`)

A Python script that uses DuckDB to store and manage stamp collection records with a two-table structure.

#### Database Structure

**Table 1: Katalog (Catalog)**
- Katalognummer (Catalog number - reference key)
- Gebiet (Region/Area)
- Jahr (Year)
- Satz (Set name/description)

**Table 2: Bestand (Inventory)**
- Katalognummer (Catalog number - foreign key to Katalog)
- Erhaltung (Condition)
- Variante (Variant)

#### Installation

```bash
pip install -r requirements.txt
```

#### Usage

Run the example demo:
```bash
python3 collector_db.py
```

Or use it as a library in your own code:

```python
from collector_db import CollectorDB

# Create database connection
with CollectorDB("my_collection.db") as db:
    # Add a catalog entry
    kat_id = db.add_katalog(
        katalognummer="DE-1849-001",
        gebiet="Deutschland",
        jahr=1849,
        satz="Bayern Schwarzer Einser"
    )
    
    # Add inventory entry referencing the catalog
    inv_id = db.add_bestand(
        katalognummer="DE-1849-001",
        erhaltung="Gestempelt",
        variante="Type I"
    )
    
    # Get all inventory with catalog info (joined)
    records = db.get_bestand_with_katalog()
    
    # Search catalog entries
    de_katalog = db.search_katalog(gebiet="Deutschland")
    
    # Get collection statistics
    stats = db.get_statistics()
```

#### Features

- Two-table structure with Katalog (catalog) and Bestand (inventory) tables
- Reference relationship between tables using Katalognummer
- Store catalog information (region, year, set) separately from physical inventory
- Search and filter by various criteria
- Get collection statistics including counts by region and condition
- Persistent storage using DuckDB
- Simple Python API with context manager support
