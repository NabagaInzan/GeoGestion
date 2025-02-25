from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
from auth.sqlite_auth import SQLiteAuth
from services.employee_service import EmployeeService
from functools import wraps
from admin.routes import admin_bp

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))  # Clé secrète pour la session

# Enregistrer le blueprint d'administration
app.register_blueprint(admin_bp)

# Initialiser les services
auth = SQLiteAuth()
employee_service = EmployeeService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return jsonify({"success": False, "error": "Non autorisé"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Établit une connexion à la base de données SQLite"""
    conn = sqlite3.connect('data/db/geogestion.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ajout des colonnes deleted_at et updated_at si elles n'existent pas
    try:
        cursor.execute("""
            ALTER TABLE employees 
            ADD COLUMN deleted_at DATETIME DEFAULT NULL;
        """)
    except:
        pass  # La colonne existe déjà

    try:
        cursor.execute("""
            ALTER TABLE employees 
            ADD COLUMN updated_at DATETIME DEFAULT NULL;
        """)
    except:
        pass

    try:
        cursor.execute("""
            ALTER TABLE contracts 
            ADD COLUMN deleted_at DATETIME DEFAULT NULL;
        """)
    except:
        pass

    try:
        cursor.execute("""
            ALTER TABLE contracts 
            ADD COLUMN updated_at DATETIME DEFAULT NULL;
        """)
    except:
        pass

    conn.commit()
    conn.close()

# Initialiser la base de données au démarrage
init_db()

@app.route('/')
def index():
    """Route principale qui affiche la page de connexion"""
    if 'operator_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/operators', methods=['GET'])
def get_operators():
    """Récupère la liste des acteurs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("SELECT * FROM operators LIMIT 1")
        row = cursor.fetchone()
        if row:
            print("Colonnes disponibles:", row.keys())
        
        cursor.execute("""
            SELECT id, name, contact1, password 
            FROM operators 
            ORDER BY name
        """)
        operators = []
        for row in cursor.fetchall():
            operators.append({
                'id': row['id'],
                'name': row['name'],
                'phone': row['contact1'],
                'password': row['password']
            })
        return jsonify({'success': True, 'operators': operators})
    except Exception as e:
        print(f"Erreur lors de la récupération des acteurs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Gère la connexion d'un opérateur"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        password = data.get('password')

        if not operator_id or not password:
            return jsonify({"success": False, "error": "ID opérateur et mot de passe requis"}), 400

        # Vérifier le mot de passe
        if auth.verify_operator_password(operator_id, password):
            # Récupérer les informations de l'opérateur
            operator = auth.get_operator_by_id(operator_id)
            if operator:
                session['operator_id'] = operator_id
                session['operator_name'] = operator['name']
                return jsonify({
                    "success": True,
                    "message": "Connexion réussie",
                    "operator": operator
                })
            
        return jsonify({
            "success": False,
            "error": "ID opérateur ou mot de passe incorrect"
        }), 401

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Affiche le tableau de bord de l'opérateur"""
    if 'operator_id' not in session:
        return redirect(url_for('index'))
    
    # Récupérer le nom de l'opérateur
    operator = auth.get_operator_by_id(session['operator_id'])
    operator_name = operator['name'] if operator else 'Inconnu'
    
    return render_template('dashboard.html', operator_name=operator_name)

@app.route('/api/employees', methods=['GET'])
@login_required
def get_employees():
    """Récupère la liste des employés de l'opérateur connecté"""
    try:
        employees = employee_service.get_employees_by_operator(session['operator_id'])
        return jsonify(employees)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/employees/<employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer les informations de l'employé
        cursor.execute("""
            SELECT e.*, 
                   c.id as contract_id, 
                   c.start_date, 
                   c.end_date, 
                   c.status as contract_status,
                   c.type as contract_type
            FROM employees e
            LEFT JOIN contracts c ON e.id = c.employee_id
            WHERE e.id = ?
            ORDER BY c.created_at DESC
            LIMIT 1
        """, (employee_id,))
        
        row = cursor.fetchone()
        if row:
            employee = {
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'position': row['position'],
                'contact': row['contact'],
                'gender': row['gender'],
                'birth_date': row['birth_date'],
                'availability': row['availability'],
                'additional_info': row['additional_info']
            }
            
            if row['contract_id']:
                employee['contract'] = {
                    'id': row['contract_id'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'status': row['contract_status'],
                    'type': row['contract_type']
                }
            
            return jsonify(employee)
        else:
            return jsonify({'error': 'Employé non trouvé'}), 404
            
    except Exception as e:
        print(f"Error getting employee: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération de l\'employé'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/employees/<employee_id>/contracts', methods=['GET'])
@login_required
def get_employee_contracts(employee_id):
    """Récupère l'historique des contrats d'un employé"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier que l'employé existe et appartient à l'opérateur connecté
        cursor.execute("""
            SELECT id, first_name, last_name 
            FROM employees 
            WHERE id = ? AND operator_id = ? AND deleted_at IS NULL
        """, (employee_id, session.get('operator_id')))
        
        employee = cursor.fetchone()
        if not employee:
            return jsonify({'error': 'Employé non trouvé'}), 404
        
        # Récupérer tous les contrats de l'employé
        cursor.execute("""
            SELECT 
                c.id,
                c.type,
                c.start_date,
                c.end_date,
                c.status,
                c.position,
                c.additional_terms
            FROM contracts c
            WHERE c.employee_id = ?
            ORDER BY c.start_date DESC
        """, (employee_id,))
        
        contracts = []
        for row in cursor.fetchall():
            contracts.append({
                'id': row['id'],
                'type': row['type'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'status': row['status'],
                'position': row['position'],
                'additional_terms': row['additional_terms']
            })
        
        return jsonify({
            'employee': {
                'id': employee['id'],
                'first_name': employee['first_name'],
                'last_name': employee['last_name']
            },
            'contracts': contracts
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des contrats: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération des contrats'}), 500
    finally:
        conn.close()

@app.route('/api/employees/<employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    conn = None
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si l'employé existe
        cursor.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Employé non trouvé'}), 404
        
        # Mise à jour de l'employé
        cursor.execute("""
            UPDATE employees 
            SET first_name = ?,
                last_name = ?,
                position = ?,
                contact = ?,
                gender = ?,
                birth_date = ?,
                availability = ?,
                additional_info = ?
            WHERE id = ?
        """, (
            data.get('first_name'),
            data.get('last_name'),
            data.get('position'),
            data.get('contact'),
            data.get('gender'),
            data.get('birth_date'),
            data.get('availability'),
            data.get('additional_info'),
            employee_id
        ))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Employé mis à jour avec succès'})
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating employee: {str(e)}")
        return jsonify({'error': 'Erreur lors de la mise à jour de l\'employé'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/employees/<employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si l'employé existe
        cursor.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Employé non trouvé'}), 404
        
        # Supprimer d'abord les contrats associés
        cursor.execute("DELETE FROM contracts WHERE employee_id = ?", (employee_id,))
        
        # Puis supprimer l'employé
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Employé supprimé avec succès'})
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error deleting employee: {str(e)}")
        return jsonify({'error': 'Erreur lors de la suppression de l\'employé'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/employees', methods=['POST'])
@login_required
def add_employee():
    """Ajoute un nouvel employé"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Données invalides"}), 400

        # Debug log pour la date de naissance
        print(f"Date de naissance reçue: {data.get('birth_date')}")

        # Ajouter l'ID de l'opérateur aux données
        data['operator_id'] = session['operator_id']
        
        # Validation des données requises
        required_fields = ['first_name', 'last_name', 'position', 'gender', 'availability']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Champs requis manquants: {', '.join(missing_fields)}"
            }), 400

        # Ajout de l'employé
        if employee_service.add_employee(data):
            return jsonify({"success": True, "message": "Employé ajouté avec succès"})
        else:
            return jsonify({"success": False, "error": "Erreur lors de l'ajout de l'employé"}), 500
            
    except Exception as e:
        print(f"Erreur lors de l'ajout d'un employé: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/employees/delete-multiple', methods=['POST'])
@login_required
def delete_multiple_employees():
    try:
        data = request.get_json()
        if not data or 'employee_ids' not in data:
            return jsonify({'error': 'Liste des employés manquante'}), 400

        employee_ids = data['employee_ids']
        if not employee_ids:
            return jsonify({'error': 'Aucun employé sélectionné'}), 400

        conn = sqlite3.connect('data/db/geogestion.db')
        cur = conn.cursor()

        try:
            # Supprimer les contrats associés
            placeholders = ','.join(['?' for _ in employee_ids])
            cur.execute(f"""
                DELETE FROM contracts 
                WHERE employee_id IN ({placeholders})
            """, employee_ids)

            # Supprimer les employés
            cur.execute(f"""
                DELETE FROM employees 
                WHERE id IN ({placeholders})
            """, employee_ids)

            conn.commit()
            return jsonify({
                'success': True,
                'message': f'{len(employee_ids)} employé(s) supprimé(s) avec succès'
            })

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            cur.close()
            conn.close()

    except Exception as e:
        print(f"Erreur lors de la suppression multiple: {str(e)}")
        return jsonify({'error': 'Erreur lors de la suppression des employés'}), 500

@app.route('/api/contracts/renew', methods=['POST'])
@login_required
def renew_contracts():
    conn = None
    try:
        data = request.get_json()
        employee_ids = data.get('employee_ids')
        start_date = data.get('start_date')
        duration = data.get('duration')
        position = data.get('position')
        availability = data.get('availability')

        if not all([employee_ids, start_date, duration, position, availability]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Calculer la date de fin
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = (start_date_obj + timedelta(days=int(duration) * 30)).strftime('%Y-%m-%d')
        except ValueError as e:
            return jsonify({'error': 'Invalid date format'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        for employee_id in employee_ids:
            # Récupérer les informations du dernier contrat
            cursor.execute("""
                SELECT type, salary, department, status
                FROM contracts 
                WHERE employee_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (employee_id,))
            
            last_contract = cursor.fetchone()
            if not last_contract:
                return jsonify({'error': f'Aucun contrat trouvé pour l\'employé {employee_id}'}), 404

            # Créer un nouveau contrat
            new_contract_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO contracts (
                    id, employee_id, type, start_date, end_date,
                    salary, department, position, status, additional_terms,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_contract_id,
                employee_id,
                last_contract['type'],
                start_date,
                end_date,
                last_contract['salary'],
                last_contract['department'],
                position,
                'En cours',
                '',  # additional_terms
                now,
                now
            ))
            
            # Mettre à jour l'employé
            cursor.execute("""
                UPDATE employees 
                SET position = ?,
                    availability = ?,
                    contract_duration = ?,
                    updated_at = ?
                WHERE id = ?
            """, (position, availability, duration, now, employee_id))

        conn.commit()
        return jsonify({'success': True, 'message': 'Contrats renouvelés avec succès'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error renewing contracts: {str(e)}")
        return jsonify({'error': 'Erreur lors du renouvellement des contrats'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/employees/renew', methods=['POST'])
@login_required
def renew_employee_contracts():
    """Renouvelle les contrats des employés sélectionnés"""
    try:
        data = request.get_json()
        employee_ids = data.get('employee_ids', [])
        
        if not employee_ids:
            return jsonify({'success': False, 'error': 'Aucun employé sélectionné'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for employee_id in employee_ids:
            # Vérifier que l'employé appartient à l'opérateur connecté
            cursor.execute("""
                SELECT id FROM employees 
                WHERE id = ? AND operator_id = ?
            """, (employee_id, session.get('operator_id')))
            
            if not cursor.fetchone():
                continue
                
            # Mettre à jour le contrat existant
            cursor.execute("""
                UPDATE contracts 
                SET status = 'Expiré'
                WHERE employee_id = ? AND status = 'En cours'
            """, (employee_id,))
            
            # Créer un nouveau contrat
            new_contract_id = str(uuid.uuid4())
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=150)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO contracts (id, employee_id, type, start_date, end_date, status)
                VALUES (?, ?, 'CDD', ?, ?, 'En cours')
            """, (new_contract_id, employee_id, start_date, end_date))
            
        conn.commit()
        return jsonify({'success': True, 'message': 'Contrats renouvelés avec succès'})
        
    except Exception as e:
        print(f"Erreur lors du renouvellement des contrats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Récupère les statistiques des employés"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        operator_id = session.get('operator_id')

        if not operator_id:
            return jsonify({"error": "Opérateur non connecté"}), 401

        # Statistiques de base
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) as male,
                SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) as female,
                SUM(CASE WHEN availability = 'Disponible' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN availability = 'Non disponible' THEN 1 ELSE 0 END) as unavailable,
                SUM(CASE 
                    WHEN birth_date IS NOT NULL 
                    AND (julianday('now') - julianday(birth_date)) / 365.25 BETWEEN 14 AND 35 
                    THEN 1 ELSE 0 END
                ) as young_employees
            FROM employees 
            WHERE operator_id = ? 
            AND deleted_at IS NULL
        """, (operator_id,))
        
        stats = cursor.fetchone()
        if stats:
            return jsonify({
                'total': stats['total'] or 0,
                'male': stats['male'] or 0,
                'female': stats['female'] or 0,
                'available': stats['available'] or 0,
                'unavailable': stats['unavailable'] or 0,
                'young_employees': stats['young_employees'] or 0
            })
        else:
            return jsonify({
                'total': 0,
                'male': 0,
                'female': 0,
                'available': 0,
                'unavailable': 0,
                'young_employees': 0
            })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération des statistiques'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/health')
def health_check():
    """Route de vérification de santé pour Render"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Change le mot de passe de l'acteur connecté"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier le mot de passe actuel
        cursor.execute("""
            SELECT password FROM operators 
            WHERE id = ? AND password = ?
        """, (session.get('operator_id'), current_password))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'}), 401
            
        # Mettre à jour le mot de passe
        cursor.execute("""
            UPDATE operators 
            SET password = ?
            WHERE id = ?
        """, (new_password, session.get('operator_id')))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Mot de passe modifié avec succès'})
        
    except Exception as e:
        print(f"Erreur lors du changement de mot de passe: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/logout')
def logout():
    """Déconnexion de l'opérateur"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
