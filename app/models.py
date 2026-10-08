from .database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash


class Product:
    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


class User:
    @staticmethod
    def register(name, email, password):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Hash password before storing it
            hashed_password = generate_password_hash(password)

            sql = """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                sql,
                (name, email, hashed_password)
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def login(email, password):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Get user by email only
            sql = "SELECT * FROM users WHERE email=%s"

            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            # Verify hashed password
            if user and check_password_hash(user["password"], password):
                return user

            return None

        finally:
            cursor.close()
            conn.close()


class Order:
    @staticmethod
    def create(user_id, items):
        """
        items:
        [
            {
                "id": 1,
                "name": "Laptop",
                "price": 799.99
            }
        ]
        """

        if not items:
            return None

        total = sum(float(p["price"]) for p in items)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Create order
            cursor.execute(
                """
                INSERT INTO orders
                (user_id, order_date, total)
                VALUES (%s, NOW(), %s)
                """,
                (user_id, total)
            )

            order_id = cursor.lastrowid

            # Add products to order
            for p in items:
                cursor.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        p["id"],
                        1,
                        p["price"]
                    )
                )

            conn.commit()

            return order_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()