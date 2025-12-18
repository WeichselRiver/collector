#!/usr/bin/env python3
"""
Collector Database - A Python script using DuckDB to store stamp collection records.
"""

import duckdb
from datetime import datetime
from typing import List, Dict, Optional


class CollectorDB:
    """A database manager for stamp collection records using DuckDB."""
    
    def __init__(self, db_path: str = "collector.db"):
        """
        Initialize the database connection and create tables.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary tables for storing records."""
        # Create sequences for auto-incrementing IDs
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_katalog_id START 1
        """)
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_bestand_id START 1
        """)
        
        # Table 1: Katalog (Catalog/Set information)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS katalog (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_katalog_id'),
                katalognummer VARCHAR NOT NULL UNIQUE,
                gebiet VARCHAR,
                jahr INTEGER,
                satz VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 2: Bestand (Inventory/Physical stamps)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bestand (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_bestand_id'),
                katalognummer VARCHAR NOT NULL,
                erhaltung VARCHAR,
                variante VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (katalognummer) REFERENCES katalog(katalognummer)
            )
        """)
    
    def add_katalog(self, katalognummer: str, gebiet: str, 
                    jahr: Optional[int] = None, satz: Optional[str] = None) -> int:
        """
        Add a new catalog entry to the database.
        
        Args:
            katalognummer: Catalog number (reference key)
            gebiet: Region/Area
            jahr: Year
            satz: Set name/description
            
        Returns:
            ID of the inserted record
        """
        result = self.conn.execute("""
            INSERT INTO katalog (katalognummer, gebiet, jahr, satz)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """, [katalognummer, gebiet, jahr, satz])
        
        return result.fetchone()[0]
    
    def add_bestand(self, katalognummer: str, erhaltung: str, 
                    variante: Optional[str] = None) -> int:
        """
        Add a new inventory/stock entry to the database.
        
        Args:
            katalognummer: Catalog number (foreign key to katalog table)
            erhaltung: Condition of the stamp
            variante: Variant
            
        Returns:
            ID of the inserted record
        """
        result = self.conn.execute("""
            INSERT INTO bestand (katalognummer, erhaltung, variante)
            VALUES (?, ?, ?)
            RETURNING id
        """, [katalognummer, erhaltung, variante])
        
        return result.fetchone()[0]
    
    def get_all_katalog(self) -> List[Dict]:
        """
        Retrieve all catalog entries from the database.
        
        Returns:
            List of dictionaries containing catalog records
        """
        result = self.conn.execute("SELECT * FROM katalog ORDER BY created_at DESC")
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def get_all_bestand(self) -> List[Dict]:
        """
        Retrieve all inventory/stock entries from the database.
        
        Returns:
            List of dictionaries containing inventory records
        """
        result = self.conn.execute("SELECT * FROM bestand ORDER BY created_at DESC")
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def get_bestand_with_katalog(self) -> List[Dict]:
        """
        Retrieve all inventory entries with their corresponding catalog information.
        
        Returns:
            List of dictionaries containing joined records
        """
        result = self.conn.execute("""
            SELECT 
                b.id as bestand_id,
                b.katalognummer,
                b.erhaltung,
                b.variante,
                k.gebiet,
                k.jahr,
                k.satz
            FROM bestand b
            LEFT JOIN katalog k ON b.katalognummer = k.katalognummer
            ORDER BY b.created_at DESC
        """)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def search_katalog(self, gebiet: Optional[str] = None, 
                      jahr: Optional[int] = None,
                      katalognummer: Optional[str] = None) -> List[Dict]:
        """
        Search for catalog entries by various criteria.
        
        Args:
            gebiet: Filter by region/area
            jahr: Filter by year
            katalognummer: Filter by catalog number
            
        Returns:
            List of matching catalog records
        """
        query = "SELECT * FROM katalog WHERE 1=1"
        params = []
        
        if gebiet:
            query += " AND gebiet = ?"
            params.append(gebiet)
        if jahr:
            query += " AND jahr = ?"
            params.append(jahr)
        if katalognummer:
            query += " AND katalognummer = ?"
            params.append(katalognummer)
        
        query += " ORDER BY jahr DESC"
        
        result = self.conn.execute(query, params)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def search_bestand(self, katalognummer: Optional[str] = None,
                      erhaltung: Optional[str] = None) -> List[Dict]:
        """
        Search for inventory entries by various criteria.
        
        Args:
            katalognummer: Filter by catalog number
            erhaltung: Filter by condition
            
        Returns:
            List of matching inventory records
        """
        query = "SELECT * FROM bestand WHERE 1=1"
        params = []
        
        if katalognummer:
            query += " AND katalognummer = ?"
            params.append(katalognummer)
        if erhaltung:
            query += " AND erhaltung = ?"
            params.append(erhaltung)
        
        result = self.conn.execute(query, params)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the stamp collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        stats = {}
        
        # Total catalog entries
        result = self.conn.execute("SELECT COUNT(*) FROM katalog")
        stats['total_katalog'] = result.fetchone()[0]
        
        # Total inventory entries
        result = self.conn.execute("SELECT COUNT(*) FROM bestand")
        stats['total_bestand'] = result.fetchone()[0]
        
        # Count by region (Gebiet)
        result = self.conn.execute("""
            SELECT gebiet, COUNT(*) as count 
            FROM katalog 
            GROUP BY gebiet 
            ORDER BY count DESC
        """)
        stats['by_gebiet'] = {row[0]: row[1] for row in result.fetchall()}
        
        # Count by condition (Erhaltung)
        result = self.conn.execute("""
            SELECT erhaltung, COUNT(*) as count 
            FROM bestand 
            GROUP BY erhaltung 
            ORDER BY count DESC
        """)
        stats['by_erhaltung'] = {row[0]: row[1] for row in result.fetchall()}
        
        return stats
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Example usage of the CollectorDB class."""
    print("=== Stamp Collector Database Demo ===\n")
    
    # Use context manager to ensure connection is closed
    with CollectorDB("collector.db") as db:
        # Add catalog entries
        print("Adding catalog entries (Katalog)...")
        kat_id1 = db.add_katalog(
            katalognummer="DE-1849-001",
            gebiet="Deutschland",
            jahr=1849,
            satz="Bayern Schwarzer Einser"
        )
        print(f"Added catalog entry with ID: {kat_id1}")
        
        kat_id2 = db.add_katalog(
            katalognummer="GB-1840-001",
            gebiet="Großbritannien",
            jahr=1840,
            satz="Penny Black"
        )
        print(f"Added catalog entry with ID: {kat_id2}")
        
        kat_id3 = db.add_katalog(
            katalognummer="DE-1850-005",
            gebiet="Deutschland",
            jahr=1850,
            satz="Preußen"
        )
        print(f"Added catalog entry with ID: {kat_id3}")
        
        # Add inventory entries
        print("\n--- Adding inventory entries (Bestand) ---")
        inv_id1 = db.add_bestand(
            katalognummer="DE-1849-001",
            erhaltung="Gestempelt",
            variante="Type I"
        )
        print(f"Added inventory entry with ID: {inv_id1}")
        
        inv_id2 = db.add_bestand(
            katalognummer="GB-1840-001",
            erhaltung="Postfrisch",
            variante=None
        )
        print(f"Added inventory entry with ID: {inv_id2}")
        
        inv_id3 = db.add_bestand(
            katalognummer="DE-1849-001",
            erhaltung="Ungebraucht",
            variante="Type II"
        )
        print(f"Added inventory entry with ID: {inv_id3}")
        
        # Retrieve all records with join
        print("\n--- All Inventory with Catalog Info ---")
        all_records = db.get_bestand_with_katalog()
        for record in all_records:
            print(f"ID {record['bestand_id']}: {record['katalognummer']} - "
                  f"{record['gebiet']} {record['jahr']} - "
                  f"Erhaltung: {record['erhaltung']}, Variante: {record['variante']}")
        
        # Search for specific catalog
        print("\n--- Deutschland Catalog Entries ---")
        de_katalog = db.search_katalog(gebiet="Deutschland")
        for kat in de_katalog:
            print(f"ID {kat['id']}: {kat['katalognummer']} - {kat['jahr']} {kat['satz']}")
        
        # Search for inventory by catalog number
        print("\n--- Inventory for DE-1849-001 ---")
        de_bestand = db.search_bestand(katalognummer="DE-1849-001")
        for inv in de_bestand:
            print(f"ID {inv['id']}: Erhaltung: {inv['erhaltung']}, Variante: {inv['variante']}")
        
        # Get statistics
        print("\n--- Collection Statistics ---")
        stats = db.get_statistics()
        print(f"Total catalog entries: {stats['total_katalog']}")
        print(f"Total inventory entries: {stats['total_bestand']}")
        print("Entries by region (Gebiet):")
        for gebiet, count in stats['by_gebiet'].items():
            print(f"  {gebiet}: {count}")
        print("Entries by condition (Erhaltung):")
        for erhaltung, count in stats['by_erhaltung'].items():
            print(f"  {erhaltung}: {count}")
    
    print("\nDatabase operations completed successfully!")


if __name__ == "__main__":
    main()
