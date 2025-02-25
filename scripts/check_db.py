import sqlite3
import os

def check_db():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, 'data', 'db', 'geogestion.db')
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Vérifier si la table existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contracts'")
    if not cur.fetchone():
        print("La table contracts n'existe pas!")
        return
    
    # Obtenir la structure de la table
    cur.execute("PRAGMA table_info(contracts)")
    columns = cur.fetchall()
    print("\nStructure de la table contracts:")
    for col in columns:
        print(f"Colonne: {col[1]}, Type: {col[2]}, Nullable: {col[3]}, Default: {col[4]}, Primary Key: {col[5]}")
    
    # Vérifier les données
    cur.execute("SELECT * FROM contracts LIMIT 1")
    row = cur.fetchone()
    if row:
        print("\nExemple de ligne:")
        print(row)
    else:
        print("\nAucune donnée dans la table")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_db()
