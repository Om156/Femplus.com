#!/usr/bin/env python3
"""
Database migration script to add TCS230 color sensor columns to the flow_readings table.
Run this script to update your existing database with the new color sensor fields.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add TCS230 color sensor columns to the flow_readings table."""
    
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
        
        # Check if color sensor columns already exist
        cursor.execute("PRAGMA table_info(flow_readings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        color_sensor_columns = [
            'color_red', 'color_green', 'color_blue', 'color_clear',
            'color_hue', 'color_saturation', 'color_brightness', 
            'color_temperature', 'color_category'
        ]
        
        # Check which columns are missing
        missing_columns = [col for col in color_sensor_columns if col not in columns]
        
        if not missing_columns:
            print("All color sensor columns already exist. No migration needed.")
            return True
        
        print(f"Adding {len(missing_columns)} color sensor columns...")
        
        # Add missing columns
        for column in missing_columns:
            if column == 'color_category':
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
    print("=" * 60)
    print("FemPlus Database Migration - TCS230 Color Sensor Integration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your FastAPI server: uvicorn app.main:app --reload")
        print("2. Test the color sensor integration in the frontend")
        print("3. Configure your TCS230 sensor to send data to ThingSpeak fields 9-16")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        print("You may need to manually add the columns or restore from backup.")

if __name__ == "__main__":
    main()
