from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

# Variável para controlar se o navegador já foi aberto
browser_opened = False

# Função para conectar ao banco de dados
def connect_db():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=localhost;'
                          'DATABASE=BANCOPI;'
                          'Trusted_Connection=yes;'
                          'Encrypt=yes;'
                          'TrustServerCertificate=yes;')
    return conn

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
        tipo_produto = request.form['tipo_produto']  # Novo campo

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
            INSERT INTO Produto (etiqueta, idModelo, idMarca, idCor, idTamanho, idEstampa, preco_unitario, tipo_produto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (etiqueta, idModelo, idMarca, idCor, idTamanho, idEstampa, preco_unitario, tipo_produto))

        conn.commit()
        conn.close()

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for('cadastrar_produto'))

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

        # Aqui você também carrega os tipos de produtos
        cursor.execute("SELECT DISTINCT tipo_produto FROM Produto")
        tipos_produto = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Renderizar o template com as opções
        return render_template('cadastrar_produto.html', 
                               modelos=modelos, 
                               marcas=marcas, 
                               cores=cores, 
                               tamanhos=tamanhos, 
                               estampas=estampas,
                               tipos_produto=tipos_produto)  # Novo campo

# (O restante do código permanece o mesmo)

# Função para abrir o navegador
def open_browser():
    global browser_opened
    if not browser_opened:
        webbrowser.open("http://127.0.0.1:5000/")  # Abre o navegador na URL
        browser_opened = True

# Iniciar o aplicativo Flask e abrir o navegador automaticamente
if __name__ == '__main__':
    threading.Thread(target=open_browser).start()  # Usar threading para abrir o navegador
    app.run(debug=True, use_reloader=False)  # Desabilitar reloader para evitar múltiplas aberturas
