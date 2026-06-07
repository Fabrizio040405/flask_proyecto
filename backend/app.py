from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

# Es vital permitir CORS para que tu frontend en Vercel pueda consultar a Render
CORS(app)

def validar_user(username : str , password : str) -> bool:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return True if user else False

@app.route('/login', methods=['POST'])
def login():
    # Recibimos los datos en formato JSON enviados por fetch()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    validar = validar_user(username, password)

    if validar:
        return jsonify({"status": "ok", "usuario": username, "message": "Login exitoso"})
    
    return jsonify({"status": "error", "message": "Usuario o contraseña incorrectas"}), 401

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    data = request.get_json()
    codigo = data.get('producto')

    if codigo and len(codigo) == 4:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            # Convertimos la tupla en un diccionario para enviarlo como JSON
            producto = {
                "id": row[0], "codigo": row[1], "nombre": row[2], 
                "descripcion": row[3], "precio": row[4], 
                "stock": row[5], "categoria": row[6]
            }
            return jsonify({"status": "ok", "data": producto})
        else:
            return jsonify({"status": "error", "message": "Producto no encontrado."}), 404

    return jsonify({"status": "error", "message": "El codigo del producto debe tener 4 caracteres."}), 400

if __name__ == '__main__':
    # Render usa '0.0.0.0' para exponer el puerto correctamente
    app.run(host='0.0.0.0', port=10000)