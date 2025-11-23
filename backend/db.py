import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create pinterest_users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pinterest_users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                pinterest_username VARCHAR(255) NOT NULL,
                pinterest_email VARCHAR(255) NOT NULL,
                pinterest_password TEXT NOT NULL,
                last_pinterest_login TIMESTAMP,
                pinterest_cookies_valid BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on user_id for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pinterest_users_user_id
            ON pinterest_users(user_id)
        """)

        conn.commit()
        logger.info("Database tables created successfully")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def save_pinterest_credentials(user_id, pinterest_username, pinterest_email, pinterest_password):
    """Save or update Pinterest credentials for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pinterest_users
                (user_id, pinterest_username, pinterest_email, pinterest_password, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id)
            DO UPDATE SET
                pinterest_username = EXCLUDED.pinterest_username,
                pinterest_email = EXCLUDED.pinterest_email,
                pinterest_password = EXCLUDED.pinterest_password,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """, (user_id, pinterest_username, pinterest_email, pinterest_password))

        result = cursor.fetchone()
        conn.commit()
        return dict(result) if result else None

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save Pinterest credentials: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_pinterest_credentials(user_id):
    """Get Pinterest credentials for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM pinterest_users WHERE user_id = %s
        """, (user_id,))

        result = cursor.fetchone()
        return dict(result) if result else None

    except Exception as e:
        logger.error(f"Failed to get Pinterest credentials: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def update_pinterest_login_status(user_id, cookies_valid):
    """Update the last login time and cookie validity status"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE pinterest_users
            SET last_pinterest_login = CURRENT_TIMESTAMP,
                pinterest_cookies_valid = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING *
        """, (cookies_valid, user_id))

        result = cursor.fetchone()
        conn.commit()
        return dict(result) if result else None

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update login status: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def delete_pinterest_credentials(user_id):
    """Delete Pinterest credentials for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM pinterest_users WHERE user_id = %s
            RETURNING user_id
        """, (user_id,))

        result = cursor.fetchone()
        conn.commit()
        return result is not None

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to delete Pinterest credentials: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()
