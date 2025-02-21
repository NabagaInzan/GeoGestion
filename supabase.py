import psycopg2

# Assurez-vous que l'URL est correcte
DATABASE_URL = "postgres://postgres:mgpYhhObJdt7TwQH@db.ytilstlgncnsiltphweo.supabase.co:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL)
    
    # Définir l'encodage de la connexion à UTF-8
    conn.set_client_encoding('UTF8')
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators")
    operators = cursor.fetchall()

    for operator in operators:
        print(operator)

    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print("Erreur lors de la connexion à la base de données:", e)
