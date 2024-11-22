import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
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
            host=db_config["host"], 
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"]
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
        cursor.execute("INSERT INTO Clientes (Nome, Email, Telefone, CPF, Endereco) VALUES (%s, %s, %s, %s, %s)",
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
        cursor.execute("UPDATE Clientes SET Nome = %s, Email = %s, Telefone = %s, CPF = %s, Endereco = %s WHERE Id = %s",
                       (nome, email, telefone, cpf, endereco, id))
        conn.commit()
        conn.close()
        flash("Cliente atualizado com sucesso!")
        return redirect(url_for('listar_clientes'))
    cursor.execute("SELECT * FROM Clientes WHERE Id = %s", (id,))
    cliente = cursor.fetchone()
    conn.close()
    return render_template('edit_cliente.html', cliente=cliente)

@app.route('/clientes/delete/<int:id>')
def excluir_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clientes WHERE Id = %s", (id,))
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
def edit_veiculo():
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        cor = request.form['cor']
        preco = request.form['preco']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Veiculos (Marca, Modelo, Ano, Cor, Preco) VALUES (%s, %s, %s, %s, %s)",
                       (marca, modelo, ano, cor, preco))
        conn.commit()
        conn.close()
        flash("Veículo criado com sucesso!")
        return redirect(url_for('listar_veiculos'))
    return render_template('create_veiculos.html')

 
@app.route('/veiculos/edit/<int:id>', methods=['GET', 'POST'])
def editar_veiculo(id):
    # Conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar o veículo por ID
    cursor.execute("SELECT * FROM Veiculos WHERE Id = %s", (id,))
    veiculo = cursor.fetchone()
    conn.close()

    if veiculo is None:
        return "Veículo não encontrado", 404

    # Caso a requisição seja POST, ou seja, após o envio do formulário
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        cor = request.form['cor']
        preco = request.form['preco']

        # Conexão com o banco para atualizar os dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Atualizar os dados no banco de dados
        cursor.execute('''UPDATE Veiculos
                          SET Marca = %s, Modelo = %s, Ano = %s, Cor = %s, Preco = %s
                          WHERE Id = %s''', (marca, modelo, ano, cor, preco, id))

        conn.commit()  # Salvar as alterações no banco
        conn.close()

        # Redirecionar para a página de listagem de veículos após a edição
        return redirect(url_for('listar_veiculos'))

    # Caso seja uma requisição GET, apenas renderiza o formulário de edição
    return render_template('edit_veiculo.html', veiculo=veiculo)

@app.route('/veiculos/delete/<int:id>')
def excluir_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Substitua o '?' por '%s'
    cursor.execute("DELETE FROM Veiculos WHERE Id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Veículo excluído com sucesso!")
    return redirect(url_for('listar_veiculos'))

@app.route('/cliente_veiculos')
def listar_associacoes():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Executando a consulta para pegar as associações de veículos
    cursor.execute('''
        SELECT cv.Id, c.Nome, v.Marca, v.Modelo, cv.Status, cv.DataRelacao
        FROM Cliente_Veiculos cv
        JOIN Clientes c ON cv.ClienteId = c.Id
        JOIN Veiculos v ON cv.VeiculoId = v.Id
    ''')

    associacoes = cursor.fetchall()  # Obtendo os dados da consulta
    conn.close()

    # Passando os dados para o template (Clientes_Veiculos agora recebe associacoes)
    return render_template('cliente_veiculos.html', Clientes_Veiculos=associacoes)


@app.route('/cliente_veiculos/create', methods=['GET', 'POST'])
def criar_cliente_veiculo():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        veiculo_id = request.form['veiculo_id']
        status = request.form['status']
        cursor.execute("INSERT INTO Cliente_Veiculos (ClienteId, VeiculoId, Status) VALUES (%s, %s, %s)",
                       (cliente_id, veiculo_id, status))
        conn.commit()
        conn.close()
        flash("Associação de Cliente e Veículo criada com sucesso!")
        return redirect(url_for('listar_associacoes'))
    
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

    # Executando a consulta para excluir a associação
    cursor.execute('DELETE FROM Cliente_Veiculos WHERE Id = %s', (id,))
    conn.commit()

    conn.close()

    # Redirecionando após a exclusão
    return redirect(url_for('listar_associacoes'))


# Importar dados
@app.route('/importar', methods=['GET', 'POST'])
def importar_dados():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado. Escolha um arquivo para importar.')
            return redirect(request.url)

        caminho = os.path.join('uploads', arquivo.filename)
        arquivo.save(caminho)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Pular cabeçalho
                for linha in reader:
                    cursor.execute(
                        "INSERT INTO Clientes (Nome, Email, Telefone, CPF, Endereco) VALUES (%s, %s, %s, %s, %s)",
                        linha
                    )
            conn.commit()
            flash("Dados importados com sucesso!")
        except Exception as e:
            flash(f"Erro ao importar dados: {e}")
        finally:
            conn.close()
            os.remove(caminho)  # Remove o arquivo após o upload

        return redirect(url_for('listar_clientes'))

    return render_template('importar.html')

# Exportar dados
# Rotas para exportação de dados
@app.route('/exportar', methods=['GET', 'POST'])
def exportar_dados():
    if request.method == 'POST':
        tipo_dado = request.form['tipo_dado']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if tipo_dado == 'clientes':
            cursor.execute("SELECT * FROM Clientes")
            rows = cursor.fetchall()
            filename = 'clientes_exportados.csv'
            headers = ['ID', 'Nome', 'Email', 'Telefone', 'CPF', 'Endereço', 'Data de Criação']
        elif tipo_dado == 'veiculos':
            cursor.execute("SELECT * FROM Veiculos")
            rows = cursor.fetchall()
            filename = 'veiculos_exportados.csv'
            headers = ['ID', 'Marca', 'Modelo', 'Ano', 'Cor', 'Preço', 'Data de Criação']
        elif tipo_dado == 'associacoes':
            query = """
            SELECT cv.Id, c.Nome AS Cliente, v.Marca AS Veiculo, cv.Status, cv.DataRelacao
            FROM Cliente_Veiculos cv
            JOIN Clientes c ON cv.ClienteId = c.Id
            JOIN Veiculos v ON cv.VeiculoId = v.Id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            filename = 'associacoes_exportadas.csv'
            headers = ['ID', 'Cliente', 'Veículo', 'Status', 'Data da Relação']
        else:
            flash("Tipo de dado inválido para exportação.")
            return redirect(url_for('exportar_dados'))
        
        # Gera o arquivo CSV
        filepath = os.path.join('exported_files', filename)
        os.makedirs('exported_files', exist_ok=True)  # Garante que a pasta existe
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Escreve os cabeçalhos
            writer.writerows(rows)  # Escreve os dados
        
        conn.close()
        return send_file(filepath, as_attachment=True)
    
    return render_template('exportar.html')

# Criar diretórios necessários
if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    app.run(debug=True)