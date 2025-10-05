#!/usr/bin/env python3
"""
Database migration script to add gas sensor columns to the flow_readings table.
Run this script to update your existing database with the new gas sensor fields.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add gas sensor columns to the flow_readings table."""
    
    # Database file path
    db_path = "swasthya_flow.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Please make sure you're running this from the project root.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Connected to database successfully.")
        
        # Check if gas sensor columns already exist
        cursor.execute("PRAGMA table_info(flow_readings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        gas_sensor_columns = [
            'co2_ppm', 'co_ppm', 'no2_ppb', 'o3_ppb', 
            'pm25_ugm3', 'pm10_ugm3', 'temperature_c', 
            'humidity_pct', 'air_quality_index', 'air_quality_category'
        ]
        
        # Check which columns are missing
        missing_columns = [col for col in gas_sensor_columns if col not in columns]
        
        if not missing_columns:
            print("All gas sensor columns already exist. No migration needed.")
            return True
        
        print(f"Adding {len(missing_columns)} gas sensor columns...")
        
        # Add missing columns
        for column in missing_columns:
            if column == 'air_quality_category':
                # String column
                cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} TEXT")
            else:
                # Float column
                cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} REAL")
            print(f"Added column: {column}")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(flow_readings)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print("\nUpdated table structure:")
        for column in updated_columns:
            print(f"  - {column}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def main():
    """Main function to run the migration."""
    print("=" * 50)
    print("FemPlus Database Migration - Gas Sensor Integration")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Set up your ThingSpeak API credentials in .env file")
        print("2. Start your FastAPI server: uvicorn app.main:app --reload")
        print("3. Test the gas sensor integration in the frontend")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        print("You may need to manually add the columns or restore from backup.")

if __name__ == "__main__":
    main()
