import sqlite3
import uuid
from datetime import datetime

class EmployeeService:
    def __init__(self):
        self.db_path = "data/db/geogestion.db"

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

    def get_employee_by_id(self, employee_id, operator_id):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, first_name, last_name, position, contact, gender,
                       contract_duration, birth_date, availability, additional_info,
                       created_at, updated_at
                FROM employees
                WHERE id = ? AND operator_id = ?
            """
            cursor.execute(query, (employee_id, operator_id))
            employee = cursor.fetchone()
            return dict(employee) if employee else None
        finally:
            conn.close()

    def add_employee(self, data):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            employee_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO employees (
                    id, first_name, last_name, position, contact, gender,
                    contract_duration, birth_date, operator_id, availability,
                    additional_info, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                employee_id,
                data.get('first_name'),
                data.get('last_name'),
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
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Vérifier que l'employé appartient à l'opérateur
            cursor.execute(
                "SELECT id FROM employees WHERE id = ? AND operator_id = ?",
                (employee_id, data.get('operator_id'))
            )
            if not cursor.fetchone():
                return False
            
            query = """
                UPDATE employees SET
                    first_name = ?,
                    last_name = ?,
                    position = ?,
                    contact = ?,
                    gender = ?,
                    contract_duration = ?,
                    birth_date = ?,
                    availability = ?,
                    additional_info = ?,
                    updated_at = ?
                WHERE id = ? AND operator_id = ?
            """
            
            cursor.execute(query, (
                data.get('first_name'),
                data.get('last_name'),
                data.get('position'),
                data.get('contact'),
                data.get('gender'),
                data.get('contract_duration'),
                data.get('birth_date'),
                data.get('availability'),
                data.get('additional_info'),
                now,
                employee_id,
                data.get('operator_id')
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_employee(self, employee_id, operator_id):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM employees WHERE id = ? AND operator_id = ?",
                (employee_id, operator_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_employee_stats(self, operator_id):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            stats = {}
            
            # Total des employés
            cursor.execute(
                "SELECT COUNT(*) as total FROM employees WHERE operator_id = ?",
                (operator_id,)
            )
            stats['total_employees'] = cursor.fetchone()[0]
            
            # Employés par genre
            cursor.execute("""
                SELECT gender, COUNT(*) as count 
                FROM employees 
                WHERE operator_id = ? 
                GROUP BY gender
            """, (operator_id,))
            stats['gender_distribution'] = dict(cursor.fetchall())
            
            # Employés par disponibilité
            cursor.execute("""
                SELECT availability, COUNT(*) as count 
                FROM employees 
                WHERE operator_id = ? 
                GROUP BY availability
            """, (operator_id,))
            stats['availability_distribution'] = dict(cursor.fetchall())
            
            # Employés par type de contrat
            cursor.execute("""
                SELECT contract_duration, COUNT(*) as count 
                FROM employees 
                WHERE operator_id = ? 
                GROUP BY contract_duration
            """, (operator_id,))
            stats['contract_distribution'] = dict(cursor.fetchall())
            
            return stats
        finally:
            conn.close()
