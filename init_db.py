import sqlite3
import os
from datetime import datetime

def init_database():
    db_path = os.path.join('data', 'db', 'geogestion.db')
    db_dir = os.path.dirname(db_path)
    
    # Créer le dossier de la base de données s'il n'existe pas
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer la table des opérateurs si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operators (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        contact1 TEXT,
        contact2 TEXT,
        email1 TEXT,
        email2 TEXT,
        address TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Créer la table des administrateurs si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS administrators (
        phone TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Ajouter l'administrateur par défaut s'il n'existe pas
    now = datetime.now().isoformat()
    cursor.execute("SELECT * FROM administrators WHERE phone = ?", ('0576610155',))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO administrators (phone, name, password, email, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('0576610155', 'Admin Principal', 'Admin123', 'admin@geogestion.com', now, now))
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès!")

if __name__ == '__main__':
    init_database()
