import sqlite3
import os
from datetime import datetime
import logging

# Configurer le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def backup_data():
    """Copie les données de la nouvelle base de données vers la sauvegarde"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, 'data', 'db', 'geogestion.db')
    backup_path = os.path.join(root_dir, 'data', 'db', 'backup', 'geogestion_backup_20250224.db')
    
    try:
        # Connexion à la nouvelle base de données
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Connexion à la base de données de sauvegarde
        backup_conn = sqlite3.connect(backup_path)
        backup_cur = backup_conn.cursor()
        
        # Recréer les tables dans la sauvegarde
        # Table employees
        backup_cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                position TEXT NOT NULL,
                contact TEXT NOT NULL,
                gender TEXT NOT NULL,
                availability TEXT NOT NULL,
                operator_id TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Table contracts
        backup_cur.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                salary DECIMAL(10, 2),
                department TEXT,
                position TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'En cours',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        
        # Vider les tables existantes dans la sauvegarde
        backup_cur.execute("DELETE FROM contracts")
        backup_cur.execute("DELETE FROM employees")
        
        # Récupérer les données de la nouvelle base
        cur.execute("SELECT * FROM employees")
        employees = cur.fetchall()
        cur.execute("PRAGMA table_info(employees)")
        employee_columns = [row[1] for row in cur.fetchall()]
        
        cur.execute("SELECT * FROM contracts")
        contracts = cur.fetchall()
        cur.execute("PRAGMA table_info(contracts)")
        contract_columns = [row[1] for row in cur.fetchall()]
        
        # Insérer les employés dans la sauvegarde
        for employee in employees:
            placeholders = ", ".join(["?" for _ in employee_columns])
            query = f"""
                INSERT INTO employees ({', '.join(employee_columns)})
                VALUES ({placeholders})
            """
            backup_cur.execute(query, employee)
        
        # Insérer les contrats dans la sauvegarde
        for contract in contracts:
            placeholders = ", ".join(["?" for _ in contract_columns])
            query = f"""
                INSERT INTO contracts ({', '.join(contract_columns)})
                VALUES ({placeholders})
            """
            backup_cur.execute(query, contract)
        
        backup_conn.commit()
        logger.info("Données sauvegardées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données : {str(e)}")
        if backup_conn:
            backup_conn.rollback()
        raise
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        if backup_cur:
            backup_cur.close()
        if backup_conn:
            backup_conn.close()

if __name__ == "__main__":
    backup_data()
