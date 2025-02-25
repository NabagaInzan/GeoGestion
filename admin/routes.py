from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from functools import wraps
from auth.sqlite_auth import SQLiteAuth
from admin.services import AdminService
import sqlite3
import os
import shutil
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
auth = SQLiteAuth()
admin_service = AdminService()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            return jsonify({"success": False, "error": "Accès administrateur requis"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Gère la connexion de l'administrateur"""
    try:
        data = request.get_json()
        phone = data.get('phone')  # 0576610155
        password = data.get('password')  # Admin123

        if not phone or not password:
            return jsonify({"success": False, "error": "Numéro de téléphone et mot de passe requis"}), 400

        # Vérifier les identifiants admin
        if auth.verify_admin_credentials(phone, password):
            session['is_admin'] = True
            return jsonify({
                "success": True,
                "message": "Connexion administrateur réussie"
            })
        
        return jsonify({
            "success": False,
            "error": "Identifiants administrateur incorrects"
        }), 401

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Affiche le tableau de bord administrateur"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/operators', methods=['GET'])
@admin_required
def get_operators():
    """Récupère la liste de tous les opérateurs"""
    try:
        operators = admin_service.get_all_operators()
        return jsonify({"success": True, "operators": operators})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/operators', methods=['POST'])
@admin_required
def add_operator():
    """Ajoute un nouvel opérateur"""
    try:
        data = request.get_json()
        result = admin_service.create_operator(data)
        return jsonify({"success": True, "operator": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/operators/<operator_id>', methods=['PUT'])
@admin_required
def update_operator(operator_id):
    """Met à jour un opérateur existant"""
    try:
        data = request.get_json()
        result = admin_service.update_operator(operator_id, data)
        return jsonify({"success": True, "operator": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/operators/<operator_id>', methods=['DELETE'])
@admin_required
def delete_operator(operator_id):
    """Supprime un opérateur"""
    try:
        admin_service.delete_operator(operator_id)
        return jsonify({"success": True, "message": "Opérateur supprimé avec succès"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/operators/<operator_id>', methods=['DELETE'])
def delete_operator_route(operator_id):
    try:
        admin_service = AdminService()
        success = admin_service.delete_operator(operator_id)
        
        if success:
            return jsonify({'message': 'Opérateur supprimé avec succès'}), 200
        else:
            return jsonify({'error': 'Opérateur non trouvé'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/administrators', methods=['GET'])
@admin_required
def get_administrators():
    """Récupère la liste de tous les administrateurs"""
    try:
        admins = auth.get_all_admins()
        return jsonify({"success": True, "administrators": admins})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/administrators/<phone>', methods=['GET'])
@admin_required
def get_administrator(phone):
    """Récupère les détails d'un administrateur"""
    try:
        admin = auth.get_admin_by_phone(phone)
        if admin:
            return jsonify({"success": True, "administrator": admin})
        return jsonify({"success": False, "error": "Administrateur non trouvé"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/administrators', methods=['POST'])
@admin_required
def add_administrator():
    """Ajoute un nouvel administrateur"""
    try:
        data = request.get_json()
        result = auth.create_admin(data)
        return jsonify({"success": True, "administrator": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/administrators/<phone>', methods=['PUT'])
@admin_required
def update_administrator(phone):
    """Met à jour un administrateur existant"""
    try:
        data = request.get_json()
        result = auth.update_admin(phone, data)
        return jsonify({"success": True, "administrator": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/administrators/<phone>', methods=['DELETE'])
@admin_required
def delete_administrator(phone):
    """Supprime un administrateur"""
    try:
        # Ne pas permettre la suppression de l'administrateur principal
        if phone == "0576610155":
            return jsonify({"success": False, "error": "Impossible de supprimer l'administrateur principal"}), 403
        
        auth.delete_admin(phone)
        return jsonify({"success": True, "message": "Administrateur supprimé avec succès"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/stats')
@admin_required
def get_stats():
    """Récupère les statistiques pour le tableau de bord"""
    try:
        conn = sqlite3.connect(auth.db_path)
        cursor = conn.cursor()
        
        # Compter les opérateurs
        cursor.execute("SELECT COUNT(*) FROM operators")
        operators_count = cursor.fetchone()[0]
        
        # Compter les administrateurs
        cursor.execute("SELECT COUNT(*) FROM administrators")
        admins_count = cursor.fetchone()[0]
        
        # Compter les employés
        cursor.execute("SELECT COUNT(*) FROM employees")
        employees_count = cursor.fetchone()[0]
        
        return jsonify({
            "success": True,
            "stats": {
                "operators_count": operators_count,
                "admins_count": admins_count,
                "employees_count": employees_count
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@admin_bp.route('/admin/database/download')
@admin_required
def download_database():
    """Télécharge une copie de la base de données"""
    try:
        file_path = admin_service.get_database_backup()
        return send_file(
            file_path,
            as_attachment=True,
            download_name='geogestion_backup.db',
            mimetype='application/x-sqlite3'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/database/backup')
@admin_required
def backup_database():
    try:
        # Créer le dossier de sauvegarde s'il n'existe pas
        backup_dir = os.path.join('data', 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Nom du fichier de sauvegarde avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'geogestion_backup_{timestamp}.db')
        
        # Copier la base de données
        shutil.copy2(os.path.join('data', 'db', 'geogestion.db'), backup_file)
        
        return send_file(
            backup_file,
            as_attachment=True,
            download_name=f'geogestion_backup_{timestamp}.db'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/database/reset', methods=['POST'])
@admin_required
def reset_database():
    try:
        # Créer une sauvegarde avant la réinitialisation
        backup_dir = os.path.join('data', 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'geogestion_backup_before_reset_{timestamp}.db')
        
        db_file = os.path.join('data', 'db', 'geogestion.db')
        if os.path.exists(db_file):
            shutil.copy2(db_file, backup_file)
            os.remove(db_file)
        
        # Réinitialiser la base de données
        from init_db import init_database
        init_database()
        
        return jsonify({'success': True, 'message': 'Base de données réinitialisée avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/logout')
def admin_logout():
    """Déconnexion de l'administrateur"""
    session.pop('is_admin', None)
    return redirect(url_for('index'))
