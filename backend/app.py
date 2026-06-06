from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# El CORS es lo que permite que Vercel se pueda comunicar con Render
CORS(app) 

def validar_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return True if user else False

# Endpoint de Login (Devuelve JSON)
@app.route('/api/login', methods=['POST'])
def api_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if validar_user(username, password):
        return jsonify({"status": "exito", "usuario": username})
    
    return jsonify({"status": "error", "mensaje": "Usuario o contraseña incorrectas"}), 401

# Endpoint del Buscador (Devuelve JSON)
@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    codigo = request.form.get('producto')

    if codigo and len(codigo) == 4:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Recuerda que esto devuelve todos los registros que coincidan, no un subset filtrado adicionalmente
        cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Producto no encontrado."}), 404

    return jsonify({"error": "El codigo del producto debe tener 4 caracteres."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=10000)