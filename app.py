from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import pymysql


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Realizo a conexão com o banco de dados - Raul Vinicius 20241118 - 11:32
db_config = {
    "host": "15.229.19.68",
    "port": 3306,          
    "user": "root", 
    "password": "@300870Sgt#",
    "database": "consultcars"
}

# Crio tabela e campos automaticamente caso não existe - Raul Vinicius 20241118 - 11:32
CREATE_DB_AND_TABLES_SCRIPT = """
CREATE DATABASE IF NOT EXISTS consultcars;
USE consultcars;

CREATE TABLE IF NOT EXISTS Clientes (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Telefone VARCHAR(15),
    CPF VARCHAR(14) NOT NULL UNIQUE,
    Endereco VARCHAR(255),
    DataCriacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Veiculos (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Marca VARCHAR(50) NOT NULL,
    Modelo VARCHAR(50) NOT NULL,
    Ano INT NOT NULL,
    Cor VARCHAR(20),
    Preco DECIMAL(10, 2),
    DataCriacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Cliente_Veiculos (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    ClienteId INT NOT NULL,
    VeiculoId INT NOT NULL,
    Status VARCHAR(50),
    DataRelacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ClienteId) REFERENCES Clientes(Id) ON DELETE CASCADE,
    FOREIGN KEY (VeiculoId) REFERENCES Veiculos(Id) ON DELETE CASCADE
);
"""


# valido se a database ja existe e crio caso necessario - Raul Vinicius 20241118 - 11:32
def ensure_database_and_tables():
    connection = None  # Inicializa a variável para evitar erros no finally
    try:
        print("Conectando ao MySQL...")
        connection = pymysql.connect(
            host=db_config["15.229.19.68"],
            port=db_config["3306"],
            user=db_config["root"],
            password=db_config["@300870Sgt#"]
        )
        print("Conexão bem-sucedida!")
        with connection.cursor() as cursor:
            print("Criando banco de dados e tabelas, se necessário...")
            for command in CREATE_DB_AND_TABLES_SCRIPT.split(";"):
                if command.strip():
                    cursor.execute(command)
        connection.commit()
        print("Banco de dados e tabelas configurados!")
    except pymysql.MySQLError as e:
        print(f"Erro ao conectar ou criar tabelas: {e}")
    finally:
        if connection:  # Fecha a conexão somente se ela foi inicializada
            connection.close()


# Conectar ao banco de dados principal
def get_db_connection():
    return pymysql.connect(**db_config)


# Garantir que o banco e tabelas existam ao iniciar o app
ensure_database_and_tables()


# Rotas e funcionalidades

## Página inicial
@app.route('/')
def index():
    return render_template('index.html')

## CRUD de Clientes
@app.route('/clientes')
def listar_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clientes")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/create', methods=['GET', 'POST'])
def criar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Clientes (Nome, Email, Telefone, CPF, Endereco) VALUES (?, ?, ?, ?, ?)",
                       (nome, email, telefone, cpf, endereco))
        conn.commit()
        conn.close()
        flash("Cliente criado com sucesso!")
        return redirect(url_for('listar_clientes'))
    return render_template('create_cliente.html')

@app.route('/clientes/edit/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        cursor.execute("UPDATE Clientes SET Nome = ?, Email = ?, Telefone = ?, CPF = ?, Endereco = ? WHERE Id = ?",
                       (nome, email, telefone, cpf, endereco, id))
        conn.commit()
        conn.close()
        flash("Cliente atualizado com sucesso!")
        return redirect(url_for('listar_clientes'))
    cursor.execute("SELECT * FROM Clientes WHERE Id = ?", (id,))
    cliente = cursor.fetchone()
    conn.close()
    return render_template('edit_cliente.html', cliente=cliente)

@app.route('/clientes/delete/<int:id>')
def excluir_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clientes WHERE Id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Cliente excluído com sucesso!")
    return redirect(url_for('listar_clientes'))

## CRUD de Veículos
@app.route('/veiculos')
def listar_veiculos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Veiculos")
    veiculos = cursor.fetchall()
    conn.close()
    return render_template('veiculos.html', veiculos=veiculos)

@app.route('/veiculos/create', methods=['GET', 'POST'])
def criar_veiculo():
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        cor = request.form['cor']
        preco = request.form['preco']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Veiculos (Marca, Modelo, Ano, Cor, Preco) VALUES (?, ?, ?, ?, ?)",
                       (marca, modelo, ano, cor, preco))
        conn.commit()
        conn.close()
        flash("Veículo criado com sucesso!")
        return redirect(url_for('listar_veiculos'))
    return render_template('create_veiculos.html')

@app.route('/veiculos/edit/<int:id>', methods=['GET', 'POST'])
def editar_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        cor = request.form['cor']
        preco = request.form['preco']
        cursor.execute("UPDATE Veiculos SET Marca = ?, Modelo = ?, Ano = ?, Cor = ?, Preco = ? WHERE Id = ?",
                       (marca, modelo, ano, cor, preco, id))
        conn.commit()
        conn.close()
        flash("Veículo atualizado com sucesso!")
        return redirect(url_for('listar_veiculos'))
    cursor.execute("SELECT * FROM Veiculos WHERE Id = ?", (id,))
    veiculo = cursor.fetchone()
    conn.close()
    return render_template('edit_veiculo.html', veiculo=veiculo)

@app.route('/veiculos/delete/<int:id>')
def excluir_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Veiculos WHERE Id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Veículo excluído com sucesso!")
    return redirect(url_for('listar_veiculos'))

## CRUD de Cliente_Veículos (alterado de associacoes para clientes_veiculos)
@app.route('/cliente_veiculos')
def listar_cliente_veiculos():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT cv.Id, c.Nome, v.Marca, v.Modelo, cv.Status, cv.DataRelacao
    FROM Cliente_Veiculos cv
    JOIN Clientes c ON cv.ClienteId = c.Id
    JOIN Veiculos v ON cv.VeiculoId = v.Id
    """
    cursor.execute(query)
    cliente_veiculos = cursor.fetchall()
    conn.close()
    return render_template('cliente_veiculos.html', cliente_veiculos=cliente_veiculos)

@app.route('/cliente_veiculos/create', methods=['GET', 'POST'])
def criar_cliente_veiculo():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        veiculo_id = request.form['veiculo_id']
        status = request.form['status']
        cursor.execute("INSERT INTO Cliente_Veiculos (ClienteId, VeiculoId, Status) VALUES (?, ?, ?)",
                       (cliente_id, veiculo_id, status))
        conn.commit()
        conn.close()
        flash("Associação de Cliente e Veículo criada com sucesso!")
        return redirect(url_for('listar_cliente_veiculos'))
    
    # Obter lista de clientes e veículos para o formulário
    cursor.execute("SELECT Id, Nome FROM Clientes")
    clientes = cursor.fetchall()
    cursor.execute("SELECT Id, Marca, Modelo FROM Veiculos")
    veiculos = cursor.fetchall()
    conn.close()
    return render_template('create_cliente_veiculos.html', clientes=clientes, veiculos=veiculos)

@app.route('/cliente_veiculos/delete/<int:id>')
def excluir_cliente_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cliente_Veiculos WHERE Id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Associação de Cliente e Veículo excluída com sucesso!")
    return redirect(url_for('listar_cliente_veiculos'))

# Inicialização
if __name__ == '__main__':
    app.run(debug=True)