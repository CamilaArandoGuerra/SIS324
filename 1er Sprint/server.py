from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sqlite3

# Configuración básica del servidor
HOST = 'localhost'
PORT = 8000

# Conexión a la base de datos SQLite
def create_db():
    conn = sqlite3.connect('eco.db')  # Archivo de base de datos
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

create_db()  # Crear la base de datos

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    # Función GET para manejar las rutas
    def do_GET(self):
        if self.path == "/login":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render_login_form().encode('utf-8'))

        elif self.path == "/users":  # Página que muestra la lista de usuarios
            users = self.get_all_users()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render_users_list(users).encode('utf-8'))

        elif self.path.startswith("/edit"):  # Página para editar un usuario
            query_components = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query_components)
            user_id = params.get('id', [None])[0]
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(self.render_edit_form(user).encode('utf-8'))
            return

        elif self.path.startswith("/delete"):  # Página para eliminar un usuario
            query_components = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query_components)
            user_id = params.get('id', [None])[0]
            if user_id:
                self.delete_user_from_db(user_id)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(self.render_success_page("Usuario eliminado con éxito").encode('utf-8'))
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]

            # Guardar el usuario en la base de datos
            self.save_user_to_db(username, password)
            
            # Obtener la lista de usuarios para mostrar
            users = self.get_all_users()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render_welcome_page(username, users).encode('utf-8'))
            
        elif self.path == "/edit":  # Manejar la edición de usuarios
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            user_id = form_data.get('id', [''])[0]
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]

            self.update_user_in_db(user_id, username, password)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render_success_page("Usuario actualizado con éxito").encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            
    # Guardar usuario en la base de datos
    def save_user_to_db(self, username, password):
        conn = sqlite3.connect('eco.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            # Usuario ya existe, se ignora
            pass
        conn.close()
        
    # Obtener usuario por ID
    def get_user_by_id(self, user_id):
        conn = sqlite3.connect('eco.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    # Actualizar usuario
    def update_user_in_db(self, user_id, username, password):
        conn = sqlite3.connect('eco.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username = ?, password = ? WHERE id = ?', (username, password, user_id))
        conn.commit()
        conn.close()
    
    # Eliminar usuario
    def delete_user_from_db(self, user_id):
        conn = sqlite3.connect('eco.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    # Renderizar el formulario de edición de usuarios
    def render_edit_form(self, user):
        user_id, username, password = user
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Editar Usuario</title>
        </head>
        <body>
            <h1>Editar Usuario</h1>
            <form method="POST" action="/edit">
                <input type="hidden" name="id" value="{user_id}">
                <label for="username">Nombre de usuario:</label>
                <input type="text" name="username" value="{username}" required><br><br>
                <label for="password">Contraseña:</label>
                <input type="password" name="password" value="{password}" required><br><br>
                <button type="submit">Actualizar</button>
            </form>
        </body>
        </html>
        """
        return html

    # Renderizar la página de éxito
    def render_success_page(self, message):
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Éxito</title>
        </head>
        <body>
            <h1>{message}</h1>
            <a href="/users">Volver a la lista de usuarios</a>
        </body>
        </html>
        """
        return html

    # Renderizar el formulario de login
    def render_login_form(self, error=None):
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Login de Usuario</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .login-container {{ background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 300px; }}
                .login-container h2 {{ text-align: center; margin-bottom: 20px; }}
                .login-container input[type="text"], .login-container input[type="password"] {{ width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }}
                .login-container button {{ width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
                .login-container button:hover {{ background-color: #45a049; }}
                .message {{ margin-top: 15px; text-align: center; color: red; }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>Iniciar Sesión</h2>
                {"<div class='message'>" + error + "</div>" if error else ""}
                <form method="POST" action="/login">
                    <input type="text" name="username" placeholder="Nombre de usuario" required>
                    <input type="password" name="password" placeholder="Contraseña" required>
                    <button type="submit">Ingresar</button>
                </form>
            </div>
        </body>
        </html>
        """
        return html

    # Renderizar la lista de usuarios
    def render_users_list(self, users):
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Lista de Usuarios</title>
        </head>
        <body>
            <h1>Usuarios Registrados</h1>
            <table border="1">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre de Usuario</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        """
        for user in users:
            html += f"""
            <tr>
                <td>{user[0]}</td>
                <td>{user[1]}</td>
                <td>
                    <a href="/edit?id={user[0]}">Editar</a> |
                    <a href="/delete?id={user[0]}" onclick="return confirm('¿Estás seguro de que deseas eliminar este usuario?');">Eliminar</a>
                </td>
            </tr>
            """
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        return html
    
    # Obtener todos los usuarios
    def get_all_users(self):
        conn = sqlite3.connect('eco.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        print("Usuarios obtenidos:", users)  # Verifica los usuarios
        return users


    def render_welcome_page(self, username, users):
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Bienvenido</title>
        </head>
        <body>
            <h1>¡Bienvenido, {username}!</h1>
            <p>Has iniciado sesión con éxito.</p>
            <h2>Lista de usuarios:</h2>
            <ul>
        """
        # Crear una lista de usuarios con enlaces de editar y eliminar
        for user in users:
            user_id, user_name, _ = user
            html += f"""
            <li>
                {user_name}
                <a href="/edit?id={user_id}">Editar</a>
                <a href="/delete?id={user_id}" onclick="return confirm('¿Estás seguro de eliminar este usuario?')">Eliminar</a>
            </li>
            """
    
        html += """
            </ul>
        </body>
        </html>
        """
        return html


if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Servidor corriendo en http://{HOST}:{PORT}/login")
    httpd.serve_forever()
