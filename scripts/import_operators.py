import csv
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = "https://dapfglvvhfkhgshwbzys.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcGZnbHZ2aGZraGdzaHdienlzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAxMzM0NTAsImV4cCI6MjA1NTcwOTQ1MH0.OIbMGVUTg22OHc3mElJ9RH7lhkL4mGhrwc43ZRCB93I"

def import_operators():
    try:
        # Lire le fichier CSV avec l'encodage latin-1
        with open('OPERATEURS.csv', 'r', encoding='latin-1') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            for row in csv_reader:
                # Préparer les données pour l'insertion
                operator_data = {
                    'name': row['NOM'].strip(),
                    'contact1': row['CONTACT 1'].strip() if row['CONTACT 1'] else None,
                    'contact2': row['CONTACT 2'].strip() if row['CONTACT 2'] else None,
                    'address1': row['ADRESSE 1'].strip() if row['ADRESSE 1'] else None,
                    'address2': row['ADRESSE 2'].strip() if row['ADRESSE 2'] else None,
                    'email1': row['E-MAIL 1'].strip() if row['E-MAIL 1'] else None,
                    'email2': row['E-MAIL 2'].strip() if row['E-MAIL 2'] else None
                }
                
                # Insérer dans la base de données via l'API REST
                response = requests.post(
                    f'{SUPABASE_URL}/rest/v1/operators',
                    headers=headers,
                    json=operator_data
                )
                
                if response.status_code == 201:
                    print(f"[OK] Opérateur ajouté : {operator_data['name']}")
                else:
                    print(f"[ERROR] Erreur lors de l'ajout de {operator_data['name']} : {response.text}")

        print("\n[SUCCESS] Tous les opérateurs ont été importés avec succès!")

    except Exception as e:
        print(f"[ERROR] Erreur lors de l'importation : {str(e)}")

if __name__ == "__main__":
    print("[START] Début de l'importation des opérateurs...")
    import_operators()
