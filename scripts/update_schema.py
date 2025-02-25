import sqlite3
import sys
from datetime import datetime
import os
def update_schema():
    conn = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'geogestion.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Créer une table temporaire avec la nouvelle structure
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees_new (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_date TEXT,
                gender TEXT CHECK(gender IN ('M', 'F')),
                position TEXT,
                contact TEXT,
                operator_id TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                status TEXT DEFAULT 'Actif',
                FOREIGN KEY (operator_id) REFERENCES operators(id)
            )
        """)

        # Copier les données de l'ancienne table vers la nouvelle
        cur.execute("""
            INSERT INTO employees_new 
            SELECT id, first_name, last_name, birth_date, gender, position, 
                   contact, operator_id, created_at, updated_at, status
            FROM employees
        """)

        # Supprimer l'ancienne table
        cur.execute("DROP TABLE employees")

        # Renommer la nouvelle table
        cur.execute("ALTER TABLE employees_new RENAME TO employees")

        conn.commit()
        print("Schema mis à jour avec succès")

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Erreur: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_schema()