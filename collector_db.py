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
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_stamps_id START 1
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS stamps (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_stamps_id'),
                country VARCHAR,
                year INTEGER,
                denomination VARCHAR,
                condition VARCHAR,
                description TEXT,
                acquired_date DATE,
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def add_stamp(self, country: str, year: int, denomination: str, 
                  condition: str, description: str = "", 
                  acquired_date: Optional[str] = None, 
                  price: Optional[float] = None) -> int:
        """
        Add a new stamp record to the database.
        
        Args:
            country: Country of origin
            year: Year of issue
            denomination: Stamp denomination/value
            condition: Condition of the stamp (e.g., 'Mint', 'Used', 'Good')
            description: Additional description
            acquired_date: Date acquired (YYYY-MM-DD format)
            price: Purchase price
            
        Returns:
            ID of the inserted record
        """
        if acquired_date is None:
            acquired_date = datetime.now().strftime('%Y-%m-%d')
        
        result = self.conn.execute("""
            INSERT INTO stamps (country, year, denomination, condition, description, acquired_date, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, [country, year, denomination, condition, description, acquired_date, price])
        
        return result.fetchone()[0]
    
    def get_all_stamps(self) -> List[Dict]:
        """
        Retrieve all stamp records from the database.
        
        Returns:
            List of dictionaries containing stamp records
        """
        result = self.conn.execute("SELECT * FROM stamps ORDER BY created_at DESC")
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def get_stamp_by_id(self, stamp_id: int) -> Optional[Dict]:
        """
        Retrieve a specific stamp record by ID.
        
        Args:
            stamp_id: The ID of the stamp to retrieve
            
        Returns:
            Dictionary containing the stamp record, or None if not found
        """
        result = self.conn.execute("SELECT * FROM stamps WHERE id = ?", [stamp_id])
        row = result.fetchone()
        if row:
            columns = [desc[0] for desc in result.description]
            return dict(zip(columns, row))
        return None
    
    def search_stamps(self, country: Optional[str] = None, 
                     year: Optional[int] = None,
                     condition: Optional[str] = None) -> List[Dict]:
        """
        Search for stamps by various criteria.
        
        Args:
            country: Filter by country
            year: Filter by year
            condition: Filter by condition
            
        Returns:
            List of matching stamp records
        """
        query = "SELECT * FROM stamps WHERE 1=1"
        params = []
        
        if country:
            query += " AND country = ?"
            params.append(country)
        if year:
            query += " AND year = ?"
            params.append(year)
        if condition:
            query += " AND condition = ?"
            params.append(condition)
        
        query += " ORDER BY year DESC"
        
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
        
        # Total count
        result = self.conn.execute("SELECT COUNT(*) FROM stamps")
        stats['total_stamps'] = result.fetchone()[0]
        
        # Count by country
        result = self.conn.execute("""
            SELECT country, COUNT(*) as count 
            FROM stamps 
            GROUP BY country 
            ORDER BY count DESC
        """)
        stats['by_country'] = {row[0]: row[1] for row in result.fetchall()}
        
        # Total value
        result = self.conn.execute("SELECT SUM(price) FROM stamps WHERE price IS NOT NULL")
        stats['total_value'] = result.fetchone()[0] or 0.0
        
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
        # Add some example stamps
        print("Adding stamp records...")
        stamp_id1 = db.add_stamp(
            country="United States",
            year=1918,
            denomination="24 cents",
            condition="Used",
            description="Inverted Jenny airmail stamp",
            price=150.00
        )
        print(f"Added stamp with ID: {stamp_id1}")
        
        stamp_id2 = db.add_stamp(
            country="United Kingdom",
            year=1840,
            denomination="1 penny",
            condition="Mint",
            description="Penny Black - first adhesive postage stamp",
            price=500.00
        )
        print(f"Added stamp with ID: {stamp_id2}")
        
        stamp_id3 = db.add_stamp(
            country="United States",
            year=1847,
            denomination="5 cents",
            condition="Good",
            description="Benjamin Franklin stamp",
            price=75.00
        )
        print(f"Added stamp with ID: {stamp_id3}")
        
        # Retrieve all stamps
        print("\n--- All Stamps ---")
        all_stamps = db.get_all_stamps()
        for stamp in all_stamps:
            print(f"ID {stamp['id']}: {stamp['year']} {stamp['country']} - {stamp['denomination']} ({stamp['condition']}) - ${stamp['price']}")
        
        # Search for stamps
        print("\n--- United States Stamps ---")
        us_stamps = db.search_stamps(country="United States")
        for stamp in us_stamps:
            print(f"ID {stamp['id']}: {stamp['year']} - {stamp['description']}")
        
        # Get statistics
        print("\n--- Collection Statistics ---")
        stats = db.get_statistics()
        print(f"Total stamps: {stats['total_stamps']}")
        print(f"Total value: ${stats['total_value']:.2f}")
        print("Stamps by country:")
        for country, count in stats['by_country'].items():
            print(f"  {country}: {count}")
    
    print("\nDatabase operations completed successfully!")


if __name__ == "__main__":
    main()
