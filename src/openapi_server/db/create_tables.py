from openapi_server.db.connection import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    tables = {}

    # MATCHES TABLE — correct, aligned to Match model + matcher.py
    tables["matches"] = """
    CREATE TABLE IF NOT EXISTS matches (
        id INT AUTO_INCREMENT PRIMARY KEY,

        donor_id VARCHAR(64) NOT NULL,
        organ_id VARCHAR(64) NOT NULL,
        recipient_id VARCHAR(64) NOT NULL,

        donor_blood_type VARCHAR(5),
        recipient_blood_type VARCHAR(5),

        organ_type VARCHAR(50),

        score FLOAT,
        status VARCHAR(20),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    for name, ddl in tables.items():
        print(f"Creating table: {name} ...")
        cur.execute(ddl)

    conn.commit()
    cur.close()
    conn.close()

    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()
