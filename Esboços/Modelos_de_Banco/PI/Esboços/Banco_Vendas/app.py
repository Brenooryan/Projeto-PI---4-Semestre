from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

# Função para conectar ao banco de dados SQL Server
def connect_db():
    return pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=LAPTOP-GNBJR3S4;'  # Altere para o nome correto do seu servidor
        r'DATABASE=BANCO_VENDAS;'  # Nome do banco de dados
        r'Trusted_Connection=yes;'
        r'Encrypt=yes;'
        r'TrustServerCertificate=yes;'
    )

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Página para registrar vendas
@app.route('/registrar-venda', methods=['GET', 'POST'])
def registrar_venda():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        produto = request.form['produto']
        quantidade = request.form['quantidade']
        preco_unitario = request.form['preco_unitario']
        data_venda = datetime.now().date()

        conn = connect_db()
        cursor = conn.cursor()

        # Inserir dados da venda no banco de dados
        cursor.execute("""
            INSERT INTO Vendas (nome_cliente, produto, quantidade, preco_unitario, data_venda)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_cliente, produto, quantidade, preco_unitario, data_venda))

        conn.commit()
        conn.close()

        flash("Venda registrada com sucesso!", "success")
        return redirect(url_for('index'))

    return render_template('registrar_venda.html')

# Função para listar vendas (opcional)
@app.route('/listar-vendas')
def listar_vendas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Vendas")
    vendas = cursor.fetchall()
    conn.close()

    # Renderiza o template e passa a lista de vendas para o template
    return render_template('listar_vendas.html', vendas=vendas)


# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)

