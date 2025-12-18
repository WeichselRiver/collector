# collector
Helpful Tools for stamp collectors

## Features

### DuckDB Storage Script (`collector_db.py`)

A Python script that uses DuckDB to store and manage stamp collection records.

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
    # Add a stamp
    stamp_id = db.add_stamp(
        country="United States",
        year=1918,
        denomination="24 cents",
        condition="Used",
        description="Inverted Jenny airmail stamp",
        price=150.00
    )
    
    # Get all stamps
    stamps = db.get_all_stamps()
    
    # Search for stamps
    us_stamps = db.search_stamps(country="United States")
    
    # Get collection statistics
    stats = db.get_statistics()
```

#### Features

- Store stamp collection records with details like country, year, denomination, condition, and price
- Search and filter stamps by various criteria
- Get collection statistics including total count and value
- Persistent storage using DuckDB
- Simple Python API with context manager support
