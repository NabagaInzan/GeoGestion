import sqlite3
import uuid
from datetime import datetime

class EmployeeService:
    def __init__(self):
        self.db_path = "data/db/geogestion.db"

    def format_name(self, name):
        """Format le nom en majuscules"""
        return name.upper() if name else ""

    def format_first_name(self, name):
        """Format le prénom avec première lettre en majuscule"""
        return name.capitalize() if name else ""

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_employees_by_operator(self, operator_id):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, first_name, last_name, position, contact, gender,
                       contract_duration, birth_date, availability, additional_info,
                       created_at, updated_at
                FROM employees
                WHERE operator_id = ?
                ORDER BY created_at DESC
            """
            cursor.execute(query, (operator_id,))
            employees = [dict(row) for row in cursor.fetchall()]
            return employees
        finally:
            conn.close()

    def get_employee_by_id(self, employee_id):
        """Récupère un employé par son ID"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, first_name, last_name, position, gender, contact, 
                       birth_date, contract_duration, availability, additional_info
                FROM employees 
                WHERE id = ?
            """, (employee_id,))
            employee = cursor.fetchone()
            conn.close()
            
            if employee:
                return {
                    'id': employee[0],
                    'first_name': employee[1],
                    'last_name': employee[2],
                    'position': employee[3],
                    'gender': employee[4],
                    'contact': employee[5],
                    'birth_date': employee[6],
                    'contract_duration': employee[7],
                    'availability': employee[8],
                    'additional_info': employee[9]
                }
            return None
        except Exception as e:
            print(f"Erreur dans get_employee_by_id: {str(e)}")
            raise e

    def add_employee(self, data):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            employee_id = str(uuid.uuid4())
            
            # Formatage des noms
            first_name = self.format_first_name(data.get('first_name', ''))
            last_name = self.format_name(data.get('last_name', ''))
            
            query = """
                INSERT INTO employees (
                    id, first_name, last_name, position, contact, gender,
                    contract_duration, birth_date, operator_id, availability,
                    additional_info, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                employee_id,
                first_name,
                last_name,
                data.get('position'),
                data.get('contact'),
                data.get('gender'),
                data.get('contract_duration'),
                data.get('birth_date'),
                data.get('operator_id'),
                data.get('availability'),
                data.get('additional_info'),
                now,
                now
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding employee: {str(e)}")
            return False
        finally:
            conn.close()

    def update_employee(self, employee_id, data):
        """Met à jour un employé"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Vérifier si l'employé existe
            cursor.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
            if not cursor.fetchone():
                conn.close()
                return False
                
            # Mettre à jour l'employé
            cursor.execute("""
                UPDATE employees 
                SET first_name = ?,
                    last_name = ?,
                    position = ?,
                    gender = ?,
                    contact = ?,
                    birth_date = ?,
                    contract_duration = ?,
                    availability = ?,
                    additional_info = ?
                WHERE id = ?
            """, (
                data.get('first_name'),
                data.get('last_name'),
                data.get('position'),
                data.get('gender'),
                data.get('contact'),
                data.get('birth_date'),
                data.get('contract_duration'),
                data.get('availability'),
                data.get('additional_info'),
                employee_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur dans update_employee: {str(e)}")
            raise e

    def delete_employee(self, employee_id):
        """Supprime un employé"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Vérifier si l'employé existe
            cursor.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
            if not cursor.fetchone():
                conn.close()
                return False
                
            # Supprimer l'employé
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur dans delete_employee: {str(e)}")
            raise e

    def get_employee_stats(self, operator_id):
        """Récupère les statistiques des employés"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Total des employés
            cursor.execute("""
                SELECT COUNT(*) 
                FROM employees 
                WHERE operator_id = ?
            """, (operator_id,))
            total = cursor.fetchone()[0]
            
            # Employés au siège
            cursor.execute("""
                SELECT COUNT(*) 
                FROM employees 
                WHERE operator_id = ? AND availability = 'Au siège'
            """, (operator_id,))
            siege = cursor.fetchone()[0]
            
            # Employés à l'intérieur
            cursor.execute("""
                SELECT COUNT(*) 
                FROM employees 
                WHERE operator_id = ? AND availability = 'À l''intérieur'
            """, (operator_id,))
            interieur = cursor.fetchone()[0]
            
            # Répartition par genre
            cursor.execute("""
                SELECT COUNT(*) 
                FROM employees 
                WHERE operator_id = ? AND gender = 'M'
            """, (operator_id,))
            male = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM employees 
                WHERE operator_id = ? AND gender = 'F'
            """, (operator_id,))
            female = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'stats': {
                    'total': total,
                    'siege': siege,
                    'interieur': interieur,
                    'male': male,
                    'female': female
                }
            }
        except Exception as e:
            print(f"Erreur dans get_employee_stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
