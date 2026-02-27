import os
from contextlib import contextmanager
from pprint import pprint
from typing import Tuple, List

from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool


load_dotenv()

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
)


@contextmanager
def get_cursor():
    conn = pool.getconn()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        pool.putconn(conn)


def fetch_tables():
    with get_cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """
            )
            return [table[0] for table in cur.fetchall()]

def fetch_table(table_name:str) -> List[Tuple[str]]:
    if table_name not in [table for table in fetch_tables()]:
        return []

    with get_cursor() as cur:
            cur.execute(
                sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            )
            res = cur.fetchall()
            return res


def fetch_user(user_id:int) -> List[Tuple[str]]:
    with get_cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE user_id=%s", (user_id,)
            )
            return cur.fetchall()[0]


def is_table_contains_column(table_name:str, column:str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = %s;",
            (table_name, column)
        )
        return bool(cur.fetchall())



if __name__ == "__main__":
    pprint(fetch_tables())
    pprint(fetch_table("users"))
    pprint(fetch_user(4))
    pprint(is_table_contains_column("users", "username"))
