from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

# Habilitamos CORS con soporte de credenciales por si se manejan cookies entre dominios
CORS(app, supports_credentials=True)

app.secret_key = 'Contraseña' 

def validar_user(username : str , password : str) -> bool:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return True if user else False

@app.route('/', methods=['GET'])
def index():
    session.clear() # Limpia la sesión
    return redirect(url_for('login'))

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return jsonify({"message": "Bienvenido, indique su usuario y contraseña"})

    # Soporta de forma segura lecturas tanto en formato JSON (fetch) como Formulario
    username = None
    password = None
    if request.is_json:
        data = request.get_json()
        if data:
            username = data.get('username')
            password = data.get('password')
    if not username:
        username = request.form.get('username')
        password = request.form.get('password')

    # Lógica de validación original
    validar = validar_user(username, password)

    if validar:
        session['usuario'] = username
        return jsonify({
            "status": "ok",
            "usuario": username,
            "message": "Login exitoso"
        })
    
    return jsonify({"status": "error", "message": "Usuario o contraseña incorrectas"}), 401

@app.route('/principal', methods=['GET'])
def principal():
    if 'usuario' in session:
        return jsonify({
            "status": "ok",
            "message": f"Bienvenido {session['usuario']} a la página principal",
            "usuario": session['usuario']
        })
    
    return jsonify({"status": "error", "message": "Debe iniciar sesión para acceder."}), 401

@app.route('/buscador', methods=['GET'])
def buscador():
    if 'usuario' in session:
        return jsonify({
            "status": "ok",
            "message": "Indique el producto a buscar: "
        })
    
    return jsonify({"status": "error", "message": "Debe iniciar sesión para acceder."}), 401

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    # Soporta la obtención del código tanto por JSON como por Formulario externo
    codigo = None
    if request.is_json:
        data = request.get_json()
        if data:
            codigo = data.get('producto')
    if not codigo:
        codigo = request.form.get('producto')

    if codigo and len(str(codigo)) == 4:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Producto no encontrado."})

    return jsonify({"error": "El codigo del producto debe tener 4 caracteres."})

@app.route('/logout', methods=['GET'])
def logout():
    session.clear() # Limpia la sesión
    return jsonify({"status": "ok", "message": "Sesión cerrada correctamente"})

if __name__ == '__main__':
    app.run(debug=True, port=10000)