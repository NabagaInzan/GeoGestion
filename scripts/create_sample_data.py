import sqlite3
import uuid
from datetime import datetime, timedelta
import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from utils.logger import logger

def create_sample_data():
    """Crée des données d'exemple pour les employés du domaine foncier"""
    db_path = os.path.join(root_dir, 'data', 'db', 'geogestion.db')
    
    # ID de l'opérateur
    operator_id = "68960c28-1b7e-4dbc-a649-db689cb326ce"
    
    # Date actuelle
    current_date = datetime.now()
    
    # Données des employés
    employees_data = [
        {
            "id": str(uuid.uuid4()),
            "first_name": "Kouamé",
            "last_name": "N'GUESSAN",
            "position": "Géomètre Expert",
            "contact": "0708091011",
            "gender": "M",
            "birth_date": "1985-06-15",
            "availability": "Sur le terrain",
            "contract_duration": "24 mois",
            "additional_info": "Expert en bornage et délimitation",
            "contract": {
                "type": "CDI",
                "start_date": (current_date - timedelta(days=400)).date(),
                "end_date": (current_date + timedelta(days=365)).date(),
                "salary": 850000,
                "department": "Topographie",
                "status": "En cours"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Amenan",
            "last_name": "KONAN",
            "position": "Juriste Foncier",
            "contact": "0102030405",
            "gender": "F",
            "birth_date": "1990-03-22",
            "availability": "Au bureau",
            "contract_duration": "12 mois",
            "additional_info": "Spécialiste en droit foncier rural",
            "contract": {
                "type": "CDD",
                "start_date": (current_date - timedelta(days=200)).date(),
                "end_date": (current_date + timedelta(days=165)).date(),
                "salary": 650000,
                "department": "Juridique",
                "status": "En cours"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Koffi",
            "last_name": "KOUASSI",
            "position": "Technicien Topographe",
            "contact": "0506070809",
            "gender": "M",
            "birth_date": "1988-11-30",
            "availability": "Sur le terrain",
            "contract_duration": "36 mois",
            "additional_info": "Expert en levés topographiques",
            "contract": {
                "type": "CDI",
                "start_date": (current_date - timedelta(days=300)).date(),
                "end_date": (current_date + timedelta(days=730)).date(),
                "salary": 550000,
                "department": "Topographie",
                "status": "En cours"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Adjoua",
            "last_name": "KOFFI",
            "position": "Assistante Administrative",
            "contact": "0708091213",
            "gender": "F",
            "birth_date": "1992-08-25",
            "availability": "Au bureau",
            "contract_duration": "12 mois",
            "additional_info": "Gestion des dossiers fonciers",
            "contract": {
                "type": "CDD",
                "start_date": (current_date - timedelta(days=150)).date(),
                "end_date": (current_date + timedelta(days=215)).date(),
                "salary": 350000,
                "department": "Administration",
                "status": "En cours"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Yao",
            "last_name": "ASSEMIEN",
            "position": "Cartographe",
            "contact": "0102030708",
            "gender": "M",
            "birth_date": "1987-04-18",
            "availability": "Au bureau",
            "contract_duration": "24 mois",
            "additional_info": "Spécialiste SIG et cartographie",
            "contract": {
                "type": "CDI",
                "start_date": (current_date - timedelta(days=250)).date(),
                "end_date": (current_date + timedelta(days=480)).date(),
                "salary": 600000,
                "department": "Cartographie",
                "status": "En cours"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Adama",
            "last_name": "COULIBALY",
            "position": "Assistant Topographe",
            "contact": "0504030201",
            "gender": "M",
            "birth_date": "1991-07-12",
            "availability": "Sur le terrain",
            "contract_duration": "6 mois",
            "additional_info": "Assistant en levés topographiques",
            "contract": {
                "type": "CDD",
                "start_date": (current_date - timedelta(days=180)).date(),
                "end_date": (current_date - timedelta(days=15)).date(),
                "salary": 300000,
                "department": "Topographie",
                "status": "Expiré"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Ahou",
            "last_name": "KOFFI",
            "position": "Secrétaire",
            "contact": "0102030405",
            "gender": "F",
            "birth_date": "1989-09-25",
            "availability": "Au bureau",
            "contract_duration": "12 mois",
            "additional_info": "Secrétaire administrative",
            "contract": {
                "type": "CDD",
                "start_date": (current_date - timedelta(days=365)).date(),
                "end_date": (current_date - timedelta(days=5)).date(),
                "salary": 250000,
                "department": "Administration",
                "status": "Expiré"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "first_name": "Bakary",
            "last_name": "DIALLO",
            "position": "Agent Cadastral",
            "contact": "0708091011",
            "gender": "M",
            "birth_date": "1986-03-18",
            "availability": "Au bureau",
            "contract_duration": "24 mois",
            "additional_info": "Spécialiste en cadastre",
            "contract": {
                "type": "CDI",
                "start_date": (current_date - timedelta(days=730)).date(),
                "end_date": (current_date - timedelta(days=30)).date(),
                "salary": 450000,
                "department": "Cadastre",
                "status": "Expiré"
            }
        }
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table des employés
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                position TEXT NOT NULL,
                contact TEXT NOT NULL,
                gender TEXT NOT NULL,
                birth_date DATE,
                availability TEXT NOT NULL,
                contract_duration TEXT,
                additional_info TEXT,
                operator_id TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Supprimer les données existantes
        cursor.execute("DELETE FROM employees WHERE operator_id = ?", (operator_id,))
        cursor.execute("DELETE FROM contracts WHERE employee_id IN (SELECT id FROM employees WHERE operator_id = ?)", (operator_id,))
        
        # Créer la table des contrats si elle n'existe pas
        cursor.execute("""
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
        
        # Insérer les employés et leurs contrats
        for employee in employees_data:
            # Insérer l'employé
            cursor.execute("""
                INSERT INTO employees (
                    id, first_name, last_name, position, contact, gender,
                    birth_date, availability, contract_duration, additional_info,
                    operator_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee["id"],
                employee["first_name"],
                employee["last_name"],
                employee["position"],
                employee["contact"],
                employee["gender"],
                employee["birth_date"],
                employee["availability"],
                employee["contract_duration"],
                employee["additional_info"],
                operator_id,
                datetime.now(),
                datetime.now()
            ))
            
            # Insérer le contrat
            contract = employee["contract"]
            cursor.execute("""
                INSERT INTO contracts (
                    id, employee_id, type, start_date, end_date,
                    salary, position, department, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                employee["id"],
                contract["type"],
                contract["start_date"],
                contract["end_date"],
                contract["salary"],
                employee["position"],
                contract["department"],
                contract["status"],
                datetime.now(),
                datetime.now()
            ))
        
        conn.commit()
        logger.info("Données d'exemple créées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des données d'exemple : {str(e)}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_sample_data()
