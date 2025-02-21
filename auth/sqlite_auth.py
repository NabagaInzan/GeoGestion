import sqlite3
import os
from typing import List, Dict, Optional

class SQLiteAuth:
    def __init__(self):
        """Initialise la connexion à la base de données SQLite"""
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'geogestion.db')

    def get_operators(self) -> List[Dict]:
        """Récupère la liste de tous les opérateurs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, contact1, email1
                FROM operators
                ORDER BY name;
            """)
            
            operators = []
            for row in cursor.fetchall():
                operators.append({
                    'id': row[0],
                    'name': row[1],
                    'contact': row[2],
                    'email': row[3]
                })
            
            return operators
            
        except Exception as e:
            print(f"Erreur lors de la récupération des opérateurs : {str(e)}")
            return []
            
        finally:
            if conn:
                conn.close()

    def verify_operator_password(self, operator_id: str, password: str) -> bool:
        """Vérifie le mot de passe d'un opérateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT password
                FROM operators
                WHERE id = ?;
            """, (operator_id,))
            
            result = cursor.fetchone()
            if result:
                return result[0] == password
            return False
            
        except Exception as e:
            print(f"Erreur lors de la vérification du mot de passe : {str(e)}")
            return False
            
        finally:
            if conn:
                conn.close()

    def get_operator_by_id(self, operator_id: str) -> Optional[Dict]:
        """Récupère les informations d'un opérateur par son ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, contact1, email1
                FROM operators
                WHERE id = ?;
            """, (operator_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'contact': row[2],
                    'email': row[3]
                }
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'opérateur : {str(e)}")
            return None
            
        finally:
            if conn:
                conn.close()
