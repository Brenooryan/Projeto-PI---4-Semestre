from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import webbrowser  # Importe o módulo webbrowser
from threading import Timer  # Importe o Timer para abrir o navegador após iniciar o servidor

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

# Função para conectar ao banco de dados
def connect_db():
    return pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};'
                          r'SERVER=LAPTOP-GNBJR3S4\SQLEX;'
                          r'DATABASE=BANCOPI;'
                          r'Trusted_Connection=yes;'
                          r'Encrypt=yes;'
                          r'TrustServerCertificate=yes;')

# Página principal com navegação
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar-produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        # Recebe os dados do formulário
        etiqueta = request.form['etiqueta']
        modelo = request.form['modelo']
        marca = request.form['marca']
        cor = request.form['cor']
        tamanho = request.form['tamanho']
        estampa = request.form['estampa']
        preco_unitario = request.form['preco_unitario']

        # Conexão com o banco de dados
        conn = connect_db()
        cursor = conn.cursor()

        # Pegando os ids das tabelas relacionadas
        cursor.execute("SELECT idModelo FROM Modelo WHERE nome_Modelo = ?", (modelo,))
        idModelo = cursor.fetchone()[0]

        cursor.execute("SELECT idMarca FROM Marca WHERE nome_Marca = ?", (marca,))
        idMarca = cursor.fetchone()[0]

        cursor.execute("SELECT idCor FROM Cor WHERE nome_Cor = ?", (cor,))
        idCor = cursor.fetchone()[0]

        cursor.execute("SELECT idTamanho FROM Tamanho WHERE tamanho = ?", (tamanho,))
        idTamanho = cursor.fetchone()[0]

        cursor.execute("SELECT idEstampa FROM Estampa WHERE tipo_Estampa = ?", (estampa,))
        idEstampa = cursor.fetchone()[0]

        # Inserir o produto no banco de dados
        cursor.execute("""
            INSERT INTO Produto (etiqueta, idModelo, idMarca, idCor, idTamanho, idEstampa, preco_unitario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (etiqueta, idModelo, idMarca, idCor, idTamanho, idEstampa, preco_unitario))

        conn.commit()
        conn.close()

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for('index'))

    else:
        # Carregar opções dinâmicas do banco de dados
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT nome_Modelo FROM Modelo")
        modelos = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT nome_Marca FROM Marca")
        marcas = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT nome_Cor FROM Cor")
        cores = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT tamanho FROM Tamanho")
        tamanhos = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT tipo_Estampa FROM Estampa")
        estampas = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Renderizar o template com as opções
        return render_template('cadastrar_produto.html', 
                               modelos=modelos, 
                               marcas=marcas, 
                               cores=cores, 
                               tamanhos=tamanhos, 
                               estampas=estampas)


# Função para abrir o navegador
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")  # URL padrão onde o Flask executa a aplicação

# Iniciar o aplicativo Flask e abrir o navegador automaticamente
if __name__ == '__main__':
    # Use o Timer para dar tempo do servidor Flask iniciar antes de abrir o navegador
    Timer(1, open_browser).start()  # Aguarda 1 segundo antes de abrir o navegador
    app.run(debug=True)
