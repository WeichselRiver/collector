# collector
Helpful Tools for stamp collectors

## Stamp Collection Recorder

A Python script that allows you to record and manage your stamp collection data using DuckDB.

### Features

- **Add stamps**: Record details about stamps in your collection (country, year, denomination, condition, price, etc.) - **Password Protected**
- **View collection**: Display all stamps with summary statistics
- **Search**: Find stamps by country or description
- **Persistent storage**: All data is stored in a local DuckDB database
- **Security**: Password protection for adding stamps to prevent unauthorized modifications

### Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

Run the script:
```bash
python collector.py
```

#### First Time Setup

On first run, you'll be prompted to set a password to protect adding stamps:

```
==================================================
FIRST TIME SETUP
==================================================
Please set a password to protect adding stamps.
Enter new password: ********
Confirm password: ********
✓ Password set successfully!
```

#### Menu Options

The script will create a `stamps.db` database file in the current directory and present you with an interactive menu:

1. **Add a new stamp** - Input details about a stamp to add it to your collection (requires password)
2. **View all stamps** - See your entire collection with statistics (no password required)
3. **Search stamps** - Find stamps by country or description (no password required)
4. **Exit** - Close the application

### Example

```
STAMP COLLECTION RECORDER
==================================================
1. Add a new stamp
2. View all stamps
3. Search stamps
4. Exit
==================================================
Select an option (1-4): 1

--- Add New Stamp ---
Enter password to add stamp: ********
✓ Password verified.
Country: United States
Year: 1950
Denomination: 3c
Condition: Used
Description (optional): Jefferson Memorial
Price paid ($): 2.50

✓ Stamp record added successfully!
```

### Security

- Adding stamps requires password authentication
- Passwords are stored as SHA-256 hashes in the database
- Only the "Add stamp" operation is protected; viewing and searching remain freely accessible
- The password is set during the first run and persists in the database

### Data Storage

All data is stored in a DuckDB database file (`stamps.db`). The database includes:
- Stamp details (country, year, denomination, condition, description)
- Acquisition date (automatically recorded)
- Price information
- Timestamps for record creation
