import sqlite3
import os

def check_columns():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, 'data', 'db', 'geogestion.db')
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Lister toutes les colonnes
    cur.execute("SELECT * FROM contracts LIMIT 1")
    column_names = [description[0] for description in cur.description]
    print("\nNoms des colonnes dans la table contracts:")
    for name in column_names:
        print(f"- {name}")
    
    # Vérifier si la colonne status existe
    cur.execute("PRAGMA table_info(contracts)")
    columns = cur.fetchall()
    print("\nInformations détaillées sur les colonnes:")
    for col in columns:
        print(f"Colonne: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, DefaultValue: {col[4]}, PK: {col[5]}")
    
    # Essayer une requête simple avec la colonne status
    try:
        cur.execute("SELECT status FROM contracts LIMIT 1")
        result = cur.fetchone()
        print("\nTest de sélection de la colonne status:", result)
    except Exception as e:
        print("\nErreur lors de la sélection de la colonne status:", str(e))
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_columns()
