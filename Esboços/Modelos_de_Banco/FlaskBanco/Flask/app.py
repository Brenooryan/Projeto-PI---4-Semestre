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

        conn.close()

        # Renderizar o template com as opções
        return render_template('cadastrar_produto.html', 
                               modelos=modelos, 
                               marcas=marcas, 
                               cores=cores, 
                               tamanhos=tamanhos, 
                               estampas=estampas)

# Rota para adicionar estoque
@app.route('/atualizar-estoque', methods=['GET', 'POST'])
def atualizar_estoque():
    if request.method == 'POST':
        etiqueta = request.form['etiqueta']
        quantidade = request.form['quantidade']

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Lógica para atualizar o estoque
            cursor.execute("SELECT quantidade FROM Estoque WHERE etiqueta = ?", (etiqueta,))
            result = cursor.fetchone()
            if result:
                nova_quantidade = result[0] + int(quantidade)
                cursor.execute("UPDATE Estoque SET quantidade = ? WHERE etiqueta = ?", (nova_quantidade, etiqueta))
            else:
                cursor.execute("INSERT INTO Estoque (etiqueta, quantidade) VALUES (?, ?)", (etiqueta, quantidade))
            conn.commit()
            flash("Estoque atualizado com sucesso!", "success")
            return redirect(url_for('atualizar_estoque'))
        except Exception as e:
            flash(f"Erro ao atualizar estoque: {str(e)}", "danger")
            conn.rollback()
        finally:
            conn.close()
    return render_template('atualizar_estoque.html')

@app.route('/registrar-venda', methods=['GET', 'POST'])
def registrar_venda():
    if request.method == 'POST':
        # Receber múltiplos itens de venda do formulário
        etiquetas = request.form.getlist('etiqueta')
        quantidades = request.form.getlist('quantidade')

        conn = connect_db()
        cursor = conn.cursor()
        try:
            valor_total = 0
            for etiqueta, quantidade in zip(etiquetas, quantidades):
                # Obter o preço unitário e quantidade disponível do estoque
                cursor.execute("""
                    SELECT preco_unitario, quantidade 
                    FROM Produto JOIN Estoque ON Produto.etiqueta = Estoque.etiqueta 
                    WHERE Produto.etiqueta = ?
                """, (etiqueta,))
                produto = cursor.fetchone()
                
                if produto:
                    preco_unitario, estoque_disponivel = produto
                    if int(quantidade) > estoque_disponivel:
                        flash(f"Estoque insuficiente para o produto {etiqueta}!", "danger")
                        conn.rollback()
                        return redirect(url_for('registrar_venda'))
                    else:
                        # Calcular o valor total da venda
                        valor_total += preco_unitario * int(quantidade)
                else:
                    flash(f"Produto com etiqueta {etiqueta} não encontrado!", "danger")
                    conn.rollback()
                    return redirect(url_for('registrar_venda'))

            # Registrar a venda na tabela Venda
            cursor.execute("INSERT INTO Venda (valor_total) VALUES (?)", (valor_total,))
            cursor.execute("SELECT @@IDENTITY AS idVenda")
            idVenda = cursor.fetchone()[0]  # Obter o ID da venda recém-criada

            # Inserir os itens na tabela ItemVenda e atualizar o estoque
            for etiqueta, quantidade in zip(etiquetas, quantidades):
                cursor.execute("""
                    SELECT preco_unitario FROM Produto WHERE etiqueta = ?
                """, (etiqueta,))
                preco_unitario = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO ItemVenda (idVenda, etiqueta, quantidade, preco_unitario) 
                    VALUES (?, ?, ?, ?)
                """, (idVenda, etiqueta, quantidade, preco_unitario))

                # Atualizar a quantidade de estoque
                cursor.execute("""
                    UPDATE Estoque SET quantidade = quantidade - ? WHERE etiqueta = ?
                """, (int(quantidade), etiqueta))

            conn.commit()
            flash("Venda registrada com sucesso!", "success")
            flash(f"Total vendido: R$ {valor_total:.2f}", "info")  # Mensagem com o total vendido
            return redirect(url_for('registrar_venda'))

        except Exception as e:
            flash(f"Erro ao registrar venda: {str(e)}", "danger")
            conn.rollback()
        finally:
            conn.close()

    return render_template('registrar_venda.html')


# Rota para cadastrar Marca, Cor, Modelo, Estampa e Tamanho
@app.route('/cadastrar-auxiliares', methods=['GET', 'POST'])
def cadastrar_auxiliares():
    if request.method == 'POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Verifica se já existe um registro com o mesmo nome
            if tipo == 'marca':
                cursor.execute("SELECT * FROM Marca WHERE nome_Marca = ?", (nome,))
                if cursor.fetchone():
                    flash(f"A marca '{nome}' já existe!", "danger")
                else:
                    cursor.execute("INSERT INTO Marca (nome_Marca) VALUES (?)", (nome,))
                    flash("Marca cadastrada com sucesso!", "success")

            elif tipo == 'cor':
                cursor.execute("SELECT * FROM Cor WHERE nome_Cor = ?", (nome,))
                if cursor.fetchone():
                    flash(f"A cor '{nome}' já existe!", "danger")
                else:
                    cursor.execute("INSERT INTO Cor (nome_Cor) VALUES (?)", (nome,))
                    flash("Cor cadastrada com sucesso!", "success")

            elif tipo == 'modelo':
                cursor.execute("SELECT * FROM Modelo WHERE nome_Modelo = ?", (nome,))
                if cursor.fetchone():
                    flash(f"O modelo '{nome}' já existe!", "danger")
                else:
                    cursor.execute("INSERT INTO Modelo (nome_Modelo) VALUES (?)", (nome,))
                    flash("Modelo cadastrado com sucesso!", "success")

            elif tipo == 'estampa':
                cursor.execute("SELECT * FROM Estampa WHERE tipo_Estampa = ?", (nome,))
                if cursor.fetchone():
                    flash(f"A estampa '{nome}' já existe!", "danger")
                else:
                    cursor.execute("INSERT INTO Estampa (tipo_Estampa) VALUES (?)", (nome,))
                    flash("Estampa cadastrada com sucesso!", "success")

            elif tipo == 'tamanho':
                cursor.execute("SELECT * FROM Tamanho WHERE tamanho = ?", (nome,))
                if cursor.fetchone():
                    flash(f"O tamanho '{nome}' já existe!", "danger")
                else:
                    cursor.execute("INSERT INTO Tamanho (tamanho) VALUES (?)", (nome,))
                    flash("Tamanho cadastrado com sucesso!", "success")

            conn.commit()
            flash(f"{tipo.capitalize()} cadastrada com sucesso!", "success")
            return redirect(url_for('cadastrar_auxiliares'))
        except Exception as e:
            flash(f"Erro ao cadastrar: {str(e)}", "danger")
            conn.rollback()
        finally:
            conn.close()
    return render_template('cadastrar_auxiliares.html')

@app.route('/consultar-vendas', methods=['GET', 'POST'])
def consultar_vendas():
    conn = connect_db()
    cursor = conn.cursor()

    # Variáveis para armazenar os filtros, agora usando GET para capturar os filtros do formulário
    data_venda = request.args.get('data_venda') if request.method == 'GET' else None
    mes_venda = request.args.get('mes_venda') if request.method == 'GET' else None
    ano_venda = request.args.get('ano_venda') if request.method == 'GET' else None

    # Montar a consulta com base nos filtros
    query_resumo = '''
        SELECT 
            V.idVenda,
            V.data_venda,
            SUM(IV.quantidade) AS total_produtos_vendidos,
            SUM(IV.quantidade * IV.preco_unitario) AS valor_total_venda
        FROM 
            Venda V
        JOIN 
            ItemVenda IV ON V.idVenda = IV.idVenda
    '''
    
    # Adicionar condições de filtro à consulta
    conditions = []
    if data_venda:
        conditions.append(f"CAST(V.data_venda AS DATE) = '{data_venda}'")
    if mes_venda:
        conditions.append(f"MONTH(V.data_venda) = {mes_venda}")
    if ano_venda:
        conditions.append(f"YEAR(V.data_venda) = {ano_venda}")

    if conditions:
        query_resumo += ' WHERE ' + ' AND '.join(conditions)

    query_resumo += '''
        GROUP BY 
            V.idVenda, V.data_venda
        ORDER BY 
            V.data_venda DESC;
    '''

    cursor.execute(query_resumo)
    vendas = cursor.fetchall()

    # Executar a segunda query para detalhar os itens vendidos
    query_detalhe = '''
        SELECT 
            V.idVenda,
            V.data_venda,
            P.etiqueta,
            M.nome_Modelo,
            Marca.nome_Marca,
            C.nome_Cor,
            T.tamanho,
            E.tipo_Estampa,
            IV.quantidade,
            IV.preco_unitario,
            IV.quantidade * IV.preco_unitario AS valor_total_item
        FROM 
            ItemVenda IV
        JOIN 
            Produto P ON IV.etiqueta = P.etiqueta
        JOIN 
            Modelo M ON P.idModelo = M.idModelo
        JOIN 
            Marca ON P.idMarca = Marca.idMarca
        JOIN 
            Cor C ON P.idCor = C.idCor
        JOIN 
            Tamanho T ON P.idTamanho = T.idTamanho
        JOIN 
            Estampa E ON P.idEstampa = E.idEstampa
        JOIN 
            Venda V ON IV.idVenda = V.idVenda
    '''
    
    if conditions:
        query_detalhe += ' WHERE ' + ' AND '.join(conditions)

    query_detalhe += ' ORDER BY V.data_venda DESC;'
    
    cursor.execute(query_detalhe)
    itens_venda = cursor.fetchall()

    conn.close()

    # Renderizar a página com os dados filtrados ou todos os dados se não houver filtros
    return render_template('consultar_vendas.html', vendas=vendas, itens_venda=itens_venda, 
                           data_venda=data_venda, mes_venda=mes_venda, ano_venda=ano_venda)



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
