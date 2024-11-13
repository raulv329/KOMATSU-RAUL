from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = "chave_secreta"

# Configuração do banco de dados MSSQL
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'CRUD_DB',
    'username': 'sa',
    'password': 'RVrv@2024',
}

def get_db_connection():
    """Retorna uma conexão com o banco de dados MSSQL."""
    conn = pyodbc.connect(
        f"DRIVER={DATABASE_CONFIG['driver']};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']}"
    )
    return conn


@app.route('/')
def index():
    """Página inicial - Lista todos os itens."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
    return render_template('index.html', items=items)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Cria um novo item."""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
        flash('Item criado com sucesso!')
        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    """Edita um item existente."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            cursor.execute("UPDATE items SET name = ?, description = ? WHERE id = ?", (name, description, item_id))
            conn.commit()
            flash('Item atualizado com sucesso!')
            return redirect(url_for('index'))
        else:
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if not item:
                flash('Item não encontrado!')
                return redirect(url_for('index'))
    return render_template('edit.html', item=item)


@app.route('/delete/<int:item_id>')
def delete(item_id):
    """Exclui um item."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    flash('Item excluído com sucesso!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
