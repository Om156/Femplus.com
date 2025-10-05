#!/usr/bin/env python3
"""
Check and fix database schema for gas sensor columns
"""

import sqlite3
import os

def check_and_fix_schema():
    db_path = "swasthya_flow.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(flow_readings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print("Current columns:")
        for col in columns:
            print(f"  - {col}")
        
        # Check if gas sensor columns exist
        gas_sensor_columns = [
            'co2_ppm', 'co_ppm', 'no2_ppb', 'o3_ppb', 
            'pm25_ugm3', 'pm10_ugm3', 'temperature_c', 'humidity_pct',
            'air_quality_index', 'air_quality_category'
        ]
        
        missing_columns = [col for col in gas_sensor_columns if col not in columns]
        
        if missing_columns:
            print(f"\nMissing gas sensor columns: {missing_columns}")
            print("Adding missing columns...")
            
            for column in missing_columns:
                if column == 'air_quality_category':
                    cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} TEXT")
                else:
                    cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} REAL")
                print(f"  Added: {column}")
            
            conn.commit()
            print("Gas sensor columns added successfully!")
        else:
            print("\nAll gas sensor columns already exist.")
        
        # Check color sensor columns
        color_sensor_columns = [
            'color_red', 'color_green', 'color_blue', 'color_clear',
            'color_hue', 'color_saturation', 'color_brightness', 
            'color_temperature', 'color_category'
        ]
        
        missing_color_columns = [col for col in color_sensor_columns if col not in columns]
        
        if missing_color_columns:
            print(f"\nMissing color sensor columns: {missing_color_columns}")
            print("Adding missing color sensor columns...")
            
            for column in missing_color_columns:
                if column == 'color_category':
                    cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} TEXT")
                else:
                    cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column} REAL")
                print(f"  Added: {column}")
            
            conn.commit()
            print("Color sensor columns added successfully!")
        else:
            print("\nAll color sensor columns already exist.")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(flow_readings)")
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"\nFinal schema has {len(final_columns)} columns:")
        for col in final_columns:
            print(f"  - {col}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Checking and fixing database schema...")
    success = check_and_fix_schema()
    if success:
        print("\n✅ Database schema updated successfully!")
    else:
        print("\n❌ Failed to update database schema.")
