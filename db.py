import psycopg2

# Database connection

def get_db_connection():
    conn = psycopg2.connect(
        host="thefruitygamedb.cj4m6k06ijo8.us-east-2.rds.amazonaws.com",
        database="postgres",
        user="watermelon",
        password="watermelon2025",
        port=5432
    )
    return conn