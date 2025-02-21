from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from dotenv import load_dotenv
from auth.sqlite_auth import SQLiteAuth
from services.employee_service import EmployeeService
from datetime import datetime
import uuid
from functools import wraps

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))  # Clé secrète pour la session

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

@app.route('/')
def index():
    """Route principale qui affiche la page de connexion"""
    if 'operator_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/operators', methods=['GET'])
def get_operators():
    """Récupère la liste des opérateurs pour l'écran de connexion"""
    try:
        operators = auth.get_operators()
        return jsonify({"success": True, "operators": operators})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
    """Récupère les détails d'un employé"""
    try:
        employee = employee_service.get_employee_by_id(employee_id, session['operator_id'])
        if employee:
            return jsonify({"success": True, "employee": employee})
        return jsonify({"success": False, "error": "Employé non trouvé"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/employees', methods=['POST'])
@login_required
def add_employee():
    """Ajoute un nouvel employé"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Données invalides"}), 400

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

@app.route('/api/employees/<employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    """Met à jour un employé existant"""
    try:
        data = request.get_json()
        data['operator_id'] = session['operator_id']
        
        if employee_service.update_employee(employee_id, data):
            return jsonify({"success": True, "message": "Employé mis à jour avec succès"})
        return jsonify({"success": False, "error": "Employé non trouvé ou non autorisé"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/employees/<employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    """Supprime un employé"""
    try:
        if employee_service.delete_employee(employee_id, session['operator_id']):
            return jsonify({"success": True, "message": "Employé supprimé avec succès"})
        return jsonify({"success": False, "error": "Employé non trouvé ou non autorisé"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Récupère les statistiques des employés pour l'opérateur connecté"""
    try:
        stats = employee_service.get_employee_stats(session['operator_id'])
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health_check():
    """Route de vérification de santé pour Render"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/logout')
def logout():
    """Déconnexion de l'opérateur"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
