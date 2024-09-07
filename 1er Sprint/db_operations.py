import sqlite3

def create_db():
    """Crea la base de datos y la tabla de usuarios si no existen."""
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    # Crear la tabla 'users' con el campo de correo electrónico
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')
    conn.commit()  # Guardar los cambios
    conn.close()   # Cerrar la conexión

def authenticate_user(username, password):
    """Verifica las credenciales del usuario en la base de datos."""
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    # Consultar la base de datos para verificar el usuario y la contraseña
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()  # Obtener el primer resultado de la consulta
    conn.close()  # Cerrar la conexión
    return user  # Devolver el usuario encontrado (o None si no se encontró)

def save_user_to_db(username, password, email):
    """Guarda un nuevo usuario en la base de datos."""
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    try:
        # Intentar insertar un nuevo usuario en la base de datos
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()  # Guardar los cambios
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")  # Imprimir error si el usuario o el correo ya existen
    conn.close()  # Cerrar la conexión

def update_user_in_db(user_id, username=None, password=None, email=None):
    """Actualiza los datos del usuario especificado por user_id."""
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    # Construir la consulta SQL para actualizar el usuario
    update_fields = []
    params = []
    
    if username:
        update_fields.append('username = ?')
        params.append(username)
    if password:
        update_fields.append('password = ?')
        params.append(password)
    if email:
        update_fields.append('email = ?')
        params.append(email)
        
    if update_fields:
        sql = f'UPDATE users SET {", ".join(update_fields)} WHERE id = ?'
        params.append(user_id)
        cursor.execute(sql, params)
        conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

def delete_user_from_db(user_id):
    """Elimina el usuario especificado por user_id de la base de datos."""
    conn = sqlite3.connect('eco.db')  # Conectar a la base de datos 'eco.db'
    cursor = conn.cursor()
    # Eliminar el usuario con el ID dado
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión
