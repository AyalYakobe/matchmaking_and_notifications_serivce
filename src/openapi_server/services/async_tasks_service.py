import json
from openapi_server.db.connection import get_connection


def create_async_task(task_id: str, match_id: int):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO async_tasks (id, match_id, status)
        VALUES (%s, %s, %s)
    """

    cur.execute(sql, (task_id, match_id, "running"))
    conn.commit()
    cur.close()
    conn.close()


def update_async_task(task_id: str, status: str, result: dict = None):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        UPDATE async_tasks
        SET status = %s, result = %s
        WHERE id = %s
    """

    cur.execute(sql, (status, json.dumps(result) if result else None, task_id))
    conn.commit()
    cur.close()
    conn.close()


def get_async_task(task_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM async_tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    return row
s