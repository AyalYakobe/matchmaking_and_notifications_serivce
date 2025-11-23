from openapi_server.db.connection import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    tables = {}

    tables["users"] = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    tables["offers"] = """
    CREATE TABLE IF NOT EXISTS offers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        organ_type VARCHAR(50),
        blood_type VARCHAR(5),
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """

    tables["matches"] = """
    CREATE TABLE IF NOT EXISTS matches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        offer_id INT NOT NULL,
        matched_user_id INT NOT NULL,
        match_score FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (offer_id) REFERENCES offers(id),
        FOREIGN KEY (matched_user_id) REFERENCES users(id)
    );
    """

    tables["notifications"] = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        message TEXT NOT NULL,
        sent BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
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
