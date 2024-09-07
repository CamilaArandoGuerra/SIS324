import sqlite3

def create_db():
    conn = sqlite3.connect('eco.db') 
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()  # Guardar los cambios
    conn.close()   # Cerrar la conexión

def authenticate_user(username, password):
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    # Consultar la base de datos para verificar el usuario y contraseña
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()  # Obtener el primer resultado de la consulta
    conn.close()  # Cerrar la conexión
    return user  # Devolver el usuario encontrado (o None si no se encontró)

def save_user_to_db(username, password):
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    try:
        # Intentar insertar un nuevo usuario en la base de datos
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()  # Guardar los cambios
    except sqlite3.IntegrityError:
        pass  # Si el usuario ya existe, ignorar el error
    conn.close()  # Cerrar la conexión
