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

def get_table_info(cursor, table_name):
    """Récupère les informations sur les colonnes d'une table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1]: row[0] for row in cursor.fetchall()}

def restore_data():
    """Copie les données de la sauvegarde vers la nouvelle base de données"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_path = os.path.join(root_dir, 'data', 'db', 'backup', 'geogestion_backup_20250224.db')
    db_path = os.path.join(root_dir, 'data', 'db', 'geogestion.db')
    
    try:
        # Connexion à la base de données de sauvegarde
        backup_conn = sqlite3.connect(backup_path)
        backup_cur = backup_conn.cursor()
        
        # Connexion à la nouvelle base de données
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Récupérer la structure des tables
        backup_employees_cols = get_table_info(backup_cur, "employees")
        backup_contracts_cols = get_table_info(backup_cur, "contracts")
        new_employees_cols = get_table_info(cur, "employees")
        new_contracts_cols = get_table_info(cur, "contracts")
        
        logger.info(f"Structure de la table employees dans la sauvegarde: {backup_employees_cols}")
        logger.info(f"Structure de la table employees dans la nouvelle BD: {new_employees_cols}")
        logger.info(f"Structure de la table contracts dans la sauvegarde: {backup_contracts_cols}")
        logger.info(f"Structure de la table contracts dans la nouvelle BD: {new_contracts_cols}")
        
        # Récupérer les employés de la sauvegarde
        backup_cur.execute("SELECT * FROM employees")
        employees = backup_cur.fetchall()
        backup_cur.execute("PRAGMA table_info(employees)")
        employee_columns = [row[1] for row in backup_cur.fetchall()]
        
        # Récupérer les contrats de la sauvegarde
        backup_cur.execute("SELECT * FROM contracts")
        contracts = backup_cur.fetchall()
        backup_cur.execute("PRAGMA table_info(contracts)")
        contract_columns = [row[1] for row in backup_cur.fetchall()]
        
        # Insérer les employés dans la nouvelle base
        for employee in employees:
            # Créer un dictionnaire avec les données de l'employé
            employee_data = dict(zip(employee_columns, employee))
            
            # Construire la requête avec seulement les colonnes qui existent dans la nouvelle table
            columns = [col for col in new_employees_cols.keys()]
            placeholders = ["?" for _ in columns]
            values = [employee_data.get(col) for col in columns]
            
            query = f"""
                INSERT OR REPLACE INTO employees (
                    {', '.join(columns)}
                ) VALUES ({', '.join(placeholders)})
            """
            cur.execute(query, values)
        
        # Insérer les contrats dans la nouvelle base
        for contract in contracts:
            # Créer un dictionnaire avec les données du contrat
            contract_data = dict(zip(contract_columns, contract))
            
            # Construire la requête avec seulement les colonnes qui existent dans la nouvelle table
            columns = [col for col in new_contracts_cols.keys()]
            placeholders = ["?" for _ in columns]
            values = [contract_data.get(col) for col in columns]
            
            query = f"""
                INSERT OR REPLACE INTO contracts (
                    {', '.join(columns)}
                ) VALUES ({', '.join(placeholders)})
            """
            cur.execute(query, values)
        
        conn.commit()
        logger.info("Données restaurées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la restauration des données : {str(e)}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if backup_cur:
            backup_cur.close()
        if backup_conn:
            backup_conn.close()
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    restore_data()
