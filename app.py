# Importa las librerías necesarias para crear la API
from flask import Flask, jsonify, request      # Flask para crear el servidor web y manejar peticiones
from flask_cors import CORS                    # Permite que otros sistemas (frontend) accedan a la API
import pymysql                                 # Librería para conectar con MySQL
import bcrypt                                  # Librería para encriptar contraseñas
from flasgger import Swagger                   # Genera documentación automática de la API

# Crea la aplicación Flask
app = Flask(__name__)

# Habilita CORS (permite peticiones desde otros dominios)
CORS(app)

# Activa Swagger para documentación de la API
swagger = Swagger(app)


# ===============================
# FUNCIÓN DE CONEXIÓN A LA BASE DE DATOS
# ===============================
def conectar(vhost, vuser, vpass, vdb):
    # Establece la conexión con la base de datos MySQL
    conn = pymysql.connect(
        host=vhost, 
        user=vuser, 
        passwd=vpass, 
        db=vdb, 
        charset='utf8mb4'
    )
    return conn


# ===============================
# RUTA: CONSULTA GENERAL (GET)
# ===============================
@app.route("/", methods=['GET'])
def consulta_general():
    """
    Consulta general del baúl de contraseñas
    """
    try:
        # Conecta a la base de datos
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')

        # Crea un cursor para ejecutar consultas
        cur = conn.cursor()

        # Ejecuta la consulta SQL
        cur.execute("SELECT * FROM baul")

        # Obtiene todos los registros
        datos = cur.fetchall()

        data = []

        # Recorre los datos y los convierte en diccionario
        for row in datos:
            dato = {
                'id_baul': row[0],
                'Plataforma': row[1],
                'usuario': row[2],
                'clave': row[3]
            }
            data.append(dato)

        # Cierra conexión
        cur.close()
        conn.close()

        # Retorna los datos en formato JSON
        return jsonify({
            'baul': data,
            'mensaje': 'Baúl de contraseñas'
        })

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# ===============================
# RUTA: CONSULTA INDIVIDUAL (GET)
# ===============================
@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):
    """
    Consulta un registro por ID
    """
    try:
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # Consulta por ID
        cur.execute(f"SELECT * FROM baul WHERE id_baul = '{codigo}'")

        datos = cur.fetchone()

        cur.close()
        conn.close()

        if datos:
            dato = {
                'id_baul': datos[0],
                'Plataforma': datos[1],
                'usuario': datos[2],
                'clave': datos[3]
            }

            return jsonify({
                'baul': dato,
                'mensaje': 'Registro encontrado'
            })

        else:
            return jsonify({
                'mensaje': 'Registro no encontrado'
            })

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# ===============================
# RUTA: REGISTRAR (POST)
# ===============================
@app.route("/registro/", methods=['POST'])
def registro():
    """
    Registrar una nueva contraseña
    """
    try:
        # Recibe los datos en formato JSON
        data = request.get_json()

        plataforma = data['plataforma']
        usuario = data['usuario']

        # Encripta la contraseña con bcrypt
        clave = bcrypt.hashpw(
            data['clave'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # Inserta el registro en la base de datos
        cur.execute(
            "INSERT INTO baul (plataforma, usuario, clave) VALUES (%s, %s, %s)",
            (plataforma, usuario, clave)
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'mensaje': 'Registro agregado'
        })

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# ===============================
# RUTA: ELIMINAR (DELETE)
# ===============================
@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    """
    Eliminar un registro por ID
    """
    try:
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # Elimina el registro
        cur.execute(
            "DELETE FROM baul WHERE id_baul = %s",
            (codigo,)
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'mensaje': 'Eliminado'
        })

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# ===============================
# RUTA: ACTUALIZAR (PUT)
# ===============================
@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):
    """
    Actualizar un registro por ID
    """
    try:
        data = request.get_json()

        plataforma = data['plataforma']
        usuario = data['usuario']

        # Encripta la nueva contraseña
        clave = bcrypt.hashpw(
            data['clave'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # Actualiza el registro
        cur.execute(
            "UPDATE baul SET plataforma = %s, usuario = %s, clave = %s WHERE id_baul = %s",
            (plataforma, usuario, clave, codigo)
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'mensaje': 'Registro actualizado'
        })

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})



# EJECUCIÓN DEL SERVIDOR

if __name__ == '__main__':
    # Inicia el servidor Flask en modo debug
    app.run(debug=True)