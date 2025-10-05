#!/usr/bin/env python3
"""
Migration script to add new parameters to the flow_readings table
"""

import sqlite3
import os

def migrate_database():
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
        
        # Add new parameter columns
        new_parameter_columns = [
            ('esr', 'REAL'),
            ('leukocyte_count', 'REAL'),
            ('vaginal_ph', 'REAL'),
            ('ca125', 'REAL'),
            ('estrogen', 'REAL'),
            ('progesterone', 'REAL'),
            ('androgens', 'REAL'),
            ('blood_glucose', 'REAL'),
            ('wbc_count', 'REAL'),
            ('pain_score', 'REAL'),
            ('weight_gain', 'REAL'),
            ('acne_severity', 'REAL'),
            ('insulin_resistance', 'REAL'),
            ('fever', 'REAL'),
            ('tenderness', 'INTEGER'),
            ('pain_during_intercourse', 'INTEGER'),
            ('bloating', 'INTEGER'),
            ('weight_loss', 'REAL'),
            ('appetite_loss', 'INTEGER'),
            ('vaginal_discharge', 'TEXT'),
            ('discharge_odor', 'TEXT'),
            ('discharge_color', 'TEXT')
        ]
        
        for column_name, column_type in new_parameter_columns:
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
    print("Migrating swasthya_flow_new.db with new parameters...")
    success = migrate_database()
    if success:
        print("\n✅ Database migration completed successfully!")
    else:
        print("\n❌ Database migration failed.")
