from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import os

app = Flask(__name__, template_folder='templates')

# ===============================
# CONFIGURACIÓN BASE DE DATOS
# ===============================
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ===============================
# CONEXIÓN A POSTGRESQL
# ===============================
def conectar_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        print("❌ Error al conectar a la base de datos:", e)
        return None


# ===============================
# CRUD
# ===============================
def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()

    if conn is None:
        print("❌ No se pudo establecer conexión")
        return

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO personas (dni, nombre, apellido, direccion, telefono)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (dni, nombre, apellido, direccion, telefono)
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_registros():
    conn = conectar_db()

    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas ORDER BY apellido")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros


def eliminar_persona(dni):
    conn = conectar_db()

    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
    conn.commit()
    cursor.close()
    conn.close()


# ===============================
# RUTAS
# ===============================
@app.route('/')
def index():
    mensaje_confirmacion = request.args.get("mensaje_confirmacion")
    return render_template('index.html', mensaje_confirmacion=mensaje_confirmacion)


@app.route('/registrar', methods=['POST'])
def registrar():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    telefono = request.form['telefono']

    crear_persona(dni, nombre, apellido, direccion, telefono)

    mensaje_confirmacion = "Registro exitoso"
    return redirect(url_for('index', mensaje_confirmacion=mensaje_confirmacion))


@app.route('/administrar')
def administrar():
    registros = obtener_registros()
    return render_template('administrar.html', registros=registros)


@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    eliminar_persona(dni)
    return redirect(url_for('administrar'))


# ===============================
# EJECUCIÓN
# ===============================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
