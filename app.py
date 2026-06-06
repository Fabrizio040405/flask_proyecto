from flask import Flask, request, render_template, url_for, redirect, session, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

CORS(app)

app.secret_key = 'Contraseña' # Se debe crear ya que no te permite utilizar
                              # el sesión sin esta clave.  

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
    username = request.form.get('username')
    password = request.form.get('password')

    validar = validar_user(username, password)

    if validar:
        session['usuario'] = username
        # Si es correcto, lo mandamos a la ventana principal en Vercel
        return redirect('https://flask-proyecto-two.vercel.app/principal.html')
    
    # Si falla, lo devolvemos al login de Vercel pero con un aviso de error en la URL
    return redirect('https://flask-proyecto-two.vercel.app/login.html?error=1')

@app.route('/principal', methods=['GET'])
def principal():
    if 'usuario' in session:
            return render_template('principal.html', message=f"Bienvenido {session['usuario']} a la página principal")
    
    return render_template('login.html', message="Debe iniciar sesión para acceder.")

@app.route('/buscador', methods=['GET'])
def buscador():
    if 'usuario' in session:
        return render_template('buscador.html', message=f"Indique el producto a buscar: ")
    
    return render_template('login.html', message="Debe iniciar sesión para acceder.")

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    codigo = request.form.get('producto')

    if codigo and len(codigo) == 4:

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
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=10000)