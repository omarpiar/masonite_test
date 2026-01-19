from masonite.controllers import Controller
import mysql.connector
import os

class DBTestController(Controller):

    def test(self):
        try:
            # 1. Conexión directa a MySQL
            conexion = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_DATABASE')
            )

            cursor = conexion.cursor()

            # 2. Inserción HARDCORE
            sql = """
                INSERT INTO usuarios_prueba (nombre, correo)
                VALUES (%s, %s)
            """
            valores = ("rafas", "rafas@gmail.com")

            cursor.execute(sql, valores)
            conexion.commit()

            # 3. Cerrar conexión
            cursor.close()
            conexion.close()

            return "Conexión exitosa. Inserción realizada correctamente."

        except Exception as e:
            return f"Error en la conexión o inserción: {e}"
