from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

browser_opened = False

# Função para conectar ao banco de dados
def connect_db():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=localhost;'
                          'DATABASE=BANCOPI2;'
                          'Trusted_Connection=yes;'
                          'Encrypt=yes;'
                          'TrustServerCertificate=yes;')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    return render_template('login.html')  # Renderiza a página de login

@app.route('/register.html', methods=['GET','POST'])
def register():
    return render_template('register.html') 

@app.route('/forgot-password.html', methods=['GET','POST'])
def forgotpassword():
    return render_template('forgot-password.html') 



# Função para abrir o navegador
def open_browser():
    global browser_opened
    if not browser_opened:
        webbrowser.open("http://127.0.0.1:5000/")  # Abre o navegador na URL
        browser_opened = True


# Iniciar o aplicativo Flask e abrir o navegador automaticamente
if __name__ == '__main__':
    threading.Thread(target=open_browser).start() 
    app.run(debug=True, use_reloader=False) 