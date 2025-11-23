from openapi_server.db.connection import get_connection

def seed_data():
    conn = get_connection()
    cur = conn.cursor()

    print("Inserting LARGE dummy dataset...")

    # ===============================
    # 1. USERS (15 entries)
    # ===============================
    users = [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Charlie Brown", "charlie@example.com"),
        ("Diana Prince", "diana@example.com"),
        ("Ethan Hunt", "ethan@example.com"),
        ("Fiona Gallagher", "fiona@example.com"),
        ("George King", "george@example.com"),
        ("Hannah Lee", "hannah@example.com"),
        ("Ian Wright", "ian@example.com"),
        ("Julia Roberts", "julia@example.com"),
        ("Kyle Anderson", "kyle@example.com"),
        ("Luna Davis", "luna@example.com"),
        ("Mason Clark", "mason@example.com"),
        ("Nina Torres", "nina@example.com"),
        ("Oscar Ramirez", "oscar@example.com"),
    ]

    cur.executemany(
        "INSERT INTO users (name, email) VALUES (%s, %s);",
        users,
    )
    print("Inserted 15 users.")

    # Map user email → user_id
    cur.execute("SELECT id, email FROM users;")
    user_map = {email: uid for uid, email in cur.fetchall()}

    # ===============================
    # 2. OFFERS (20 entries)
    # ===============================
    offers = [
        (user_map["alice@example.com"], "kidney", "A+", "pending"),
        (user_map["bob@example.com"], "liver", "O-", "accepted"),
        (user_map["charlie@example.com"], "heart", "B+", "pending"),
        (user_map["diana@example.com"], "lung", "AB+", "pending"),
        (user_map["ethan@example.com"], "kidney", "A-", "declined"),
        (user_map["fiona@example.com"], "liver", "O+", "pending"),
        (user_map["george@example.com"], "heart", "B-", "expired"),
        (user_map["hannah@example.com"], "kidney", "A+", "pending"),
        (user_map["ian@example.com"], "lung", "AB-", "accepted"),
        (user_map["julia@example.com"], "liver", "O-", "pending"),
        (user_map["kyle@example.com"], "kidney", "A+", "pending"),
        (user_map["luna@example.com"], "heart", "B+", "accepted"),
        (user_map["mason@example.com"], "kidney", "A-", "pending"),
        (user_map["nina@example.com"], "liver", "O-", "pending"),
        (user_map["oscar@example.com"], "kidney", "A+", "expired"),
        (user_map["alice@example.com"], "heart", "B+", "pending"),
        (user_map["charlie@example.com"], "liver", "O+", "accepted"),
        (user_map["fiona@example.com"], "kidney", "A-", "pending"),
        (user_map["hannah@example.com"], "liver", "O-", "declined"),
        (user_map["mason@example.com"], "lung", "AB+", "pending"),
    ]

    cur.executemany(
        "INSERT INTO offers (user_id, organ_type, blood_type, status) VALUES (%s, %s, %s, %s);",
        offers
    )
    print("Inserted 20 offers.")

    # Fetch offer IDs
    cur.execute("SELECT id FROM offers;")
    offer_ids = [row[0] for row in cur.fetchall()]

    # ===============================
    # 3. MATCHES (12 entries)
    # ===============================
    matches = [
        (offer_ids[0],  user_map["bob@example.com"],      95.2),
        (offer_ids[1],  user_map["charlie@example.com"],  88.5),
        (offer_ids[2],  user_map["alice@example.com"],    90.1),
        (offer_ids[3],  user_map["ethan@example.com"],    72.4),
        (offer_ids[4],  user_map["diana@example.com"],    84.0),
        (offer_ids[5],  user_map["hannah@example.com"],   79.6),
        (offer_ids[6],  user_map["luna@example.com"],     93.1),
        (offer_ids[7],  user_map["julia@example.com"],    87.3),
        (offer_ids[8],  user_map["kyle@example.com"],     90.9),
        (offer_ids[9],  user_map["mason@example.com"],    68.4),
        (offer_ids[10], user_map["nina@example.com"],     88.2),
        (offer_ids[11], user_map["oscar@example.com"],    91.7),
    ]

    cur.executemany(
        "INSERT INTO matches (offer_id, matched_user_id, match_score) VALUES (%s, %s, %s);",
        matches
    )
    print("Inserted 12 matches.")

    # ===============================
    # 4. NOTIFICATIONS (25 entries)
    # ===============================
    notifications = [
        (user_map["alice@example.com"], "Your organ offer has been received.", False),
        (user_map["bob@example.com"], "A potential match was found!", False),
        (user_map["charlie@example.com"], "You have a new match offer.", False),
        (user_map["diana@example.com"], "Your offer is under review.", True),
        (user_map["ethan@example.com"], "Match expired.", True),
        (user_map["fiona@example.com"], "Recipient accepted your offer.", False),
        (user_map["george@example.com"], "You have a pending liver match.", False),
        (user_map["hannah@example.com"], "Organ offer updated.", True),
        (user_map["ian@example.com"], "New match available.", False),
        (user_map["julia@example.com"], "Your offer has been declined.", True),
        (user_map["kyle@example.com"], "Your match score is high!", False),
        (user_map["luna@example.com"], "Organ allocation notification.", False),
        (user_map["mason@example.com"], "Your offer is now pending.", False),
        (user_map["nina@example.com"], "A potential match has been identified.", True),
        (user_map["oscar@example.com"], "Recipient declined your offer.", True),

        # Extra 10 notifications
        (user_map["alice@example.com"], "Reminder: update your donor profile.", False),
        (user_map["bob@example.com"], "Match window is closing soon.", False),
        (user_map["charlie@example.com"], "Organ compatibility verified.", False),
        (user_map["diana@example.com"], "Your recipient responded.", False),
        (user_map["ethan@example.com"], "Action required: confirm details.", False),
        (user_map["fiona@example.com"], "Hospital has reviewed your offer.", True),
        (user_map["george@example.com"], "You received a new message.", False),
        (user_map["hannah@example.com"], "Offer processing complete.", True),
        (user_map["ian@example.com"], "Please check your status update.", False),
        (user_map["julia@example.com"], "Your match is being evaluated.", False),
    ]

    cur.executemany(
        "INSERT INTO notifications (user_id, message, sent) VALUES (%s, %s, %s);",
        notifications
    )
    print("Inserted 25 notifications.")

    # ===============================
    # COMMIT + CLOSE
    # ===============================
    conn.commit()
    cur.close()
    conn.close()

    print("\n🎉 LARGE dummy dataset inserted successfully!")


if __name__ == "__main__":
    seed_data()
