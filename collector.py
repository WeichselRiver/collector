#!/usr/bin/env python3
"""
Collector - A data recorder for stamp collectors using DuckDB
This script allows users to input and store information about their stamp collection.
"""

import duckdb
import sys
import hashlib
import getpass
from datetime import datetime
from pathlib import Path


class StampCollector:
    """Main class for managing stamp collection data with DuckDB"""
    
    def __init__(self, db_path="stamps.db"):
        """Initialize the database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create the stamps table if it doesn't exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS stamps (
                id INTEGER PRIMARY KEY,
                country VARCHAR,
                year INTEGER,
                denomination VARCHAR,
                condition VARCHAR,
                description TEXT,
                acquisition_date DATE,
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS stamp_id_seq START 1
        """)
        # Create a table to store the password hash
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR PRIMARY KEY,
                value VARCHAR
            )
        """)
    
    def add_stamp(self, country, year, denomination, condition, description, price):
        """Add a new stamp record to the database"""
        try:
            acquisition_date = datetime.now().date()
            self.conn.execute("""
                INSERT INTO stamps (id, country, year, denomination, condition, description, acquisition_date, price)
                VALUES (nextval('stamp_id_seq'), ?, ?, ?, ?, ?, ?, ?)
            """, [country, year, denomination, condition, description, acquisition_date, price])
            print("\n✓ Stamp record added successfully!")
            return True
        except Exception as e:
            print(f"\n✗ Error adding stamp: {e}")
            return False
    
    def view_all_stamps(self):
        """Display all stamps in the collection"""
        try:
            result = self.conn.execute("""
                SELECT id, country, year, denomination, condition, price, acquisition_date
                FROM stamps
                ORDER BY id DESC
            """).fetchall()
            
            if not result:
                print("\nNo stamps in the collection yet.")
                return
            
            print("\n" + "="*80)
            print("STAMP COLLECTION")
            print("="*80)
            print(f"{'ID':<5} {'Country':<15} {'Year':<6} {'Denom.':<10} {'Cond.':<10} {'Price':<10} {'Date':<12}")
            print("-"*80)
            
            for row in result:
                print(f"{row[0]:<5} {row[1]:<15} {row[2]:<6} {row[3]:<10} {row[4]:<10} ${row[5]:<9.2f} {row[6]}")
            
            print("="*80)
            
            # Show summary statistics
            stats = self.conn.execute("""
                SELECT COUNT(*), SUM(price), AVG(price)
                FROM stamps
            """).fetchone()
            
            total_value = stats[1] if stats[1] is not None else 0
            avg_value = stats[2] if stats[2] is not None else 0
            print(f"\nTotal Stamps: {stats[0]} | Total Value: ${total_value:.2f} | Average Value: ${avg_value:.2f}")
            
        except Exception as e:
            print(f"\n✗ Error viewing stamps: {e}")
    
    def search_stamps(self, search_term):
        """Search for stamps by country or description"""
        try:
            result = self.conn.execute("""
                SELECT id, country, year, denomination, condition, description, price
                FROM stamps
                WHERE country LIKE ? OR description LIKE ?
                ORDER BY id DESC
            """, [f"%{search_term}%", f"%{search_term}%"]).fetchall()
            
            if not result:
                print(f"\nNo stamps found matching '{search_term}'.")
                return
            
            print(f"\n{'ID':<5} {'Country':<15} {'Year':<6} {'Denom.':<10} {'Cond.':<10} {'Price':<10}")
            print("-"*70)
            
            for row in result:
                print(f"{row[0]:<5} {row[1]:<15} {row[2]:<6} {row[3]:<10} {row[4]:<10} ${row[6]:<9.2f}")
                if row[5]:
                    print(f"      Description: {row[5]}")
            
        except Exception as e:
            print(f"\n✗ Error searching stamps: {e}")
    
    def close(self):
        """Close the database connection"""
        self.conn.close()
    
    def _hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_password_set(self):
        """Check if a password has been set"""
        result = self.conn.execute("""
            SELECT value FROM settings WHERE key = 'password_hash'
        """).fetchone()
        return result is not None
    
    def set_password(self, password):
        """Set the password for adding stamps"""
        password_hash = self._hash_password(password)
        # Use INSERT OR REPLACE to handle both new and existing passwords
        self.conn.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES ('password_hash', ?)
        """, [password_hash])
        return True
    
    def verify_password(self, password):
        """Verify if the provided password matches the stored hash"""
        password_hash = self._hash_password(password)
        result = self.conn.execute("""
            SELECT value FROM settings WHERE key = 'password_hash'
        """).fetchone()
        
        if result is None:
            return False
        
        return result[0] == password_hash


def get_user_input(prompt, input_type=str, required=True):
    """Helper function to get and validate user input"""
    while True:
        try:
            value = input(prompt).strip()
            
            if not value and required:
                print("This field is required. Please enter a value.")
                continue
            
            if not value and not required:
                return None
            
            if input_type == int:
                return int(value)
            elif input_type == float:
                return float(value)
            else:
                return value
                
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None


def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("STAMP COLLECTION RECORDER")
    print("="*50)
    print("1. Add a new stamp")
    print("2. View all stamps")
    print("3. Search stamps")
    print("4. Exit")
    print("="*50)


def main():
    """Main application loop"""
    print("Welcome to Stamp Collection Recorder!")
    print("Database will be stored in: stamps.db")
    
    collector = StampCollector()
    
    # Check if password is set, if not, prompt to set it
    if not collector.is_password_set():
        print("\n" + "="*50)
        print("FIRST TIME SETUP")
        print("="*50)
        print("Please set a password to protect adding stamps.")
        while True:
            password = getpass.getpass("Enter new password: ")
            if not password:
                print("Password cannot be empty. Please try again.")
                continue
            confirm_password = getpass.getpass("Confirm password: ")
            if password == confirm_password:
                collector.set_password(password)
                print("✓ Password set successfully!")
                break
            else:
                print("✗ Passwords do not match. Please try again.")
    
    try:
        while True:
            print_menu()
            choice = get_user_input("Select an option (1-4): ")
            
            if choice == "1":
                # Add new stamp - requires password
                print("\n--- Add New Stamp ---")
                
                # Verify password before allowing to add stamp
                password = getpass.getpass("Enter password to add stamp: ")
                if not collector.verify_password(password):
                    print("\n✗ Incorrect password. Cannot add stamp.")
                    continue
                
                print("✓ Password verified.")
                
                country = get_user_input("Country: ")
                if country is None:
                    continue
                
                year = get_user_input("Year: ", int)
                if year is None:
                    continue
                
                denomination = get_user_input("Denomination (e.g., 10c, $1): ")
                if denomination is None:
                    continue
                
                condition = get_user_input("Condition (Mint/Used/Fair/Poor): ")
                if condition is None:
                    continue
                
                description = get_user_input("Description (optional): ", required=False)
                
                price = get_user_input("Price paid ($): ", float)
                if price is None:
                    continue
                
                collector.add_stamp(country, year, denomination, condition, description or "", price)
            
            elif choice == "2":
                # View all stamps
                collector.view_all_stamps()
            
            elif choice == "3":
                # Search stamps
                search_term = get_user_input("Enter search term (country or description): ")
                if search_term:
                    collector.search_stamps(search_term)
            
            elif choice == "4":
                # Exit
                print("\nThank you for using Stamp Collection Recorder!")
                break
            
            else:
                print("\nInvalid option. Please select 1-4.")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        collector.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
