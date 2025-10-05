#!/usr/bin/env python3
"""
Fix the swasthya_flow_new.db database schema
"""

import sqlite3
import os

def fix_database():
    db_path = "swasthya_flow_new.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(flow_readings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print("Current columns in swasthya_flow_new.db:")
        for col in columns:
            print(f"  - {col}")
        
        # Add gas sensor columns
        gas_sensor_columns = [
            ('co2_ppm', 'REAL'),
            ('co_ppm', 'REAL'),
            ('no2_ppb', 'REAL'),
            ('o3_ppb', 'REAL'),
            ('pm25_ugm3', 'REAL'),
            ('pm10_ugm3', 'REAL'),
            ('temperature_c', 'REAL'),
            ('humidity_pct', 'REAL'),
            ('air_quality_index', 'REAL'),
            ('air_quality_category', 'TEXT')
        ]
        
        for column_name, column_type in gas_sensor_columns:
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column_name} {column_type}")
                print(f"  Added: {column_name}")
            else:
                print(f"  Already exists: {column_name}")
        
        # Add color sensor columns
        color_sensor_columns = [
            ('color_red', 'REAL'),
            ('color_green', 'REAL'),
            ('color_blue', 'REAL'),
            ('color_clear', 'REAL'),
            ('color_hue', 'REAL'),
            ('color_saturation', 'REAL'),
            ('color_brightness', 'REAL'),
            ('color_temperature', 'REAL'),
            ('color_category', 'TEXT')
        ]
        
        for column_name, column_type in color_sensor_columns:
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE flow_readings ADD COLUMN {column_name} {column_type}")
                print(f"  Added: {column_name}")
            else:
                print(f"  Already exists: {column_name}")
        
        conn.commit()
        
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
    print("Fixing swasthya_flow_new.db database schema...")
    success = fix_database()
    if success:
        print("\n✅ Database schema updated successfully!")
    else:
        print("\n❌ Failed to update database schema.")
