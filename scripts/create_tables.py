from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = "https://dapfglvvhfkhgshwbzys.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcGZnbHZ2aGZraGdzaHdienlzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAxMzM0NTAsImV4cCI6MjA1NTcwOTQ1MH0.OIbMGVUTg22OHc3mElJ9RH7lhkL4mGhrwc43ZRCB93I"

# Créer le client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_tables():
    try:
        # SQL pour créer les tables et les politiques
        sql = """
        -- Extension pour UUID
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- Table operators
        CREATE TABLE IF NOT EXISTS operators (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(255) NOT NULL,
            contact1 VARCHAR(255),
            contact2 VARCHAR(255),
            address1 VARCHAR(255),
            address2 VARCHAR(255),
            email1 VARCHAR(255),
            email2 VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Activer RLS pour la table operators
        ALTER TABLE operators ENABLE ROW LEVEL SECURITY;

        -- Politique pour permettre l'insertion à tous les utilisateurs authentifiés
        DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON operators;
        CREATE POLICY "Enable insert for authenticated users only"
        ON operators FOR INSERT
        TO authenticated
        WITH CHECK (true);

        -- Politique pour permettre la lecture à tous les utilisateurs authentifiés
        DROP POLICY IF EXISTS "Enable read access for authenticated users only" ON operators;
        CREATE POLICY "Enable read access for authenticated users only"
        ON operators FOR SELECT
        TO authenticated
        USING (true);

        -- Politique pour permettre la mise à jour aux utilisateurs authentifiés
        DROP POLICY IF EXISTS "Enable update for authenticated users only" ON operators;
        CREATE POLICY "Enable update for authenticated users only"
        ON operators FOR UPDATE
        TO authenticated
        USING (true)
        WITH CHECK (true);

        -- Table users
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table employees
        CREATE TABLE IF NOT EXISTS employees (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            contact VARCHAR(255),
            gender VARCHAR(50),
            contract_duration VARCHAR(255),
            birth_date DATE,
            operator_id UUID REFERENCES operators(id),
            availability VARCHAR(255),
            salary DECIMAL(10,2),
            additional_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table action_logs
        CREATE TABLE IF NOT EXISTS action_logs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id),
            action TEXT NOT NULL,
            target_table TEXT NOT NULL,
            target_record_id UUID,
            action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table roles
        CREATE TABLE IF NOT EXISTS roles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            role_name VARCHAR(255) NOT NULL,
            description TEXT
        );
        """

        # Exécuter le SQL
        supabase.table('operators').rpc('exec_sql', {'query': sql}).execute()
        print("[OK] Tables et politiques créées avec succès")

        # Insertion des rôles par défaut
        roles_sql = """
        INSERT INTO roles (role_name, description)
        VALUES 
            ('admin', 'Administrateur de l''application'),
            ('operateur', 'Opérateur responsable de la gestion des employés')
        ON CONFLICT (role_name) DO NOTHING;
        """
        
        supabase.table('roles').rpc('exec_sql', {'query': roles_sql}).execute()
        print("[OK] Rôles par défaut créés avec succès")

        print("\n[SUCCESS] Configuration de la base de données terminée!")

    except Exception as e:
        print(f"[ERROR] Erreur lors de la création des tables: {str(e)}")

if __name__ == "__main__":
    print("[START] Début de la création des tables...")
    create_tables()
