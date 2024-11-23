from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pyodbc
import webbrowser
import threading


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para gerenciar sessões

# Função para conectar ao banco de dados
def connect_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=BANCOPIFIM;'
        'Trusted_Connection=yes;'
        'Encrypt=yes;'
        'TrustServerCertificate=yes;'
    )
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Verifica se as chaves existem no formulário
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error="Por favor, preencha todos os campos.")
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT idUsuario FROM Usuario WHERE username = ? AND senha = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username  # Armazena o nome do usuário na sessão
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuário ou senha inválidos!")
    
    return render_template('login.html')

# Página do dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = session['user']
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

# Rota para logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))

# ========================
# GERENCIAR PRODUTOS
# ========================

@app.route('/gerenciar_produtos')
def gerenciar_produtos():
    # Conexão ao banco para pegar as informações do estoque
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT P.etiqueta, C.nome_Categoria AS categoria, S.nome_SubCategoria AS subcategoria, 
               M.nome_Modelo AS modelo, Marca.nome_Marca AS marca, Cor.nome_Cor AS cor, 
               T.nome_Tamanho AS tamanho, Est.tipo_Estampa AS estampa, P.preco_unitario, E.quantidade
        FROM Produto P
        JOIN Categoria C ON P.idCategoria = C.idCategoria
        JOIN SubCategoria S ON P.idSubCategoria = S.idSubCategoria
        JOIN Modelo M ON P.idModelo = M.idModelo
        JOIN Marca ON P.idMarca = Marca.idMarca
        JOIN Cor ON P.idCor = Cor.idCor
        JOIN Estoque E ON P.etiqueta = E.etiqueta
        JOIN Tamanho T ON E.idTamanho = T.idTamanho
        JOIN Estampa Est ON P.idEstampa = Est.idEstampa
        """
    )
    estoque = cursor.fetchall()
    conn.close()

    # Verifica se a consulta retornou dados
    if not estoque:
        estoque = []

    return render_template('gerenciar_produtos.html', estoque=estoque)

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        etiqueta = request.form['etiqueta']
        categoria = request.form['categoria']
        subcategoria = request.form['subcategoria']
        modelo = request.form['modelo']
        marca = request.form['marca']
        cor = request.form['cor']
        estampa = request.form['estampa']
        preco = request.form['preco']

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Verificar se a etiqueta já existe
            cursor.execute("SELECT etiqueta FROM Produto WHERE etiqueta = ?", (etiqueta,))
            if cursor.fetchone():
                return render_template('cadastrar_produto.html', error="Etiqueta já cadastrada.")
            
            # Inserir o produto no banco
            cursor.execute(
                """
                INSERT INTO Produto (etiqueta, idCategoria, idSubCategoria, idModelo, idMarca, idCor, idEstampa, preco_unitario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (etiqueta, categoria, subcategoria, modelo, marca, cor, estampa, preco)
            )
            conn.commit()
            
            # Mensagem de sucesso após cadastro
            success_message = "Produto cadastrado com sucesso!"
            return render_template('cadastrar_produto.html', success=success_message)

        except Exception as e:
            conn.rollback()
            return render_template('cadastrar_produto.html', error=str(e))
        finally:
            conn.close()

    # Carregar dados para preencher as opções do formulário (categorias, subcategorias, etc.)
    conn = connect_db()
    cursor = conn.cursor()

    # Buscar categorias
    cursor.execute("SELECT idCategoria, nome_Categoria FROM Categoria")
    categorias = cursor.fetchall()

    # Buscar modelos, marcas, cores e estampas
    cursor.execute("SELECT idModelo, nome_Modelo FROM Modelo")
    modelos = cursor.fetchall()

    cursor.execute("SELECT idMarca, nome_Marca FROM Marca")
    marcas = cursor.fetchall()

    cursor.execute("SELECT idCor, nome_Cor FROM Cor")
    cores = cursor.fetchall()

    cursor.execute("SELECT idEstampa, tipo_Estampa FROM Estampa")
    estampas = cursor.fetchall()

    # Buscar subcategorias com base na categoria selecionada, se houver
    categoria_selecionada = request.args.get('categoria')  # Pega o id da categoria selecionada
    subcategoria_selecionada = request.args.get('subcategoria')  # Pega o id da subcategoria selecionada

    subcategorias = []
    if categoria_selecionada:
        cursor.execute(
            "SELECT idSubCategoria, nome_SubCategoria FROM SubCategoria WHERE idCategoria = ?",
            (categoria_selecionada,)
        )
        subcategorias = cursor.fetchall()

    conn.close()

    return render_template('cadastrar_produto.html', categorias=categorias, subcategorias=subcategorias, 
                           modelos=modelos, marcas=marcas, cores=cores, estampas=estampas,
                           categoria_selecionada=categoria_selecionada, subcategoria_selecionada=subcategoria_selecionada)


# Rota para carregar subcategorias via AJAX
@app.route('/subcategorias/<int:categoria_id>', methods=['GET'])
def get_subcategorias(categoria_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Buscar subcategorias relacionadas à categoria
    cursor.execute(
        "SELECT idSubCategoria, nome_SubCategoria FROM SubCategoria WHERE idCategoria = ?",
        (categoria_id,)
    )
    subcategorias = cursor.fetchall()
    conn.close()
    
    # Converter os dados em um formato JSON
    subcategorias_list = [{"idSubCategoria": subcategoria[0], "nome_SubCategoria": subcategoria[1]} for subcategoria in subcategorias]
    
    return jsonify(subcategorias_list)


@app.route('/visualizar_estoque')
def visualizar_estoque():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT P.etiqueta, C.nome_Categoria AS categoria, S.nome_SubCategoria AS subcategoria, 
               M.nome_Modelo AS modelo, Marca.nome_Marca AS marca, Cor.nome_Cor AS cor, 
               T.nome_Tamanho AS tamanho, Est.tipo_Estampa AS estampa, P.preco_unitario, E.quantidade
        FROM Produto P
        JOIN Categoria C ON P.idCategoria = C.idCategoria
        JOIN SubCategoria S ON P.idSubCategoria = S.idSubCategoria
        JOIN Modelo M ON P.idModelo = M.idModelo
        JOIN Marca ON P.idMarca = Marca.idMarca
        JOIN Cor ON P.idCor = Cor.idCor
        JOIN Estoque E ON P.etiqueta = E.etiqueta
        JOIN Tamanho T ON E.idTamanho = T.idTamanho
        JOIN Estampa Est ON P.idEstampa = Est.idEstampa
        """
    )
    estoque = cursor.fetchall()
    conn.close()
    
    # Verifica se a consulta retornou dados
    if not estoque:
        estoque = []

    return render_template('visualizar_estoque.html', estoque=estoque)

@app.route('/atualizar_estoque', methods=['GET', 'POST'])
def atualizar_estoque():
    tamanhos = obter_tamanhos()  # Obtém os tamanhos de produto do banco
    
    if request.method == 'POST':
        etiqueta = request.form['etiqueta']
        tamanho = request.form['tamanho']  # Aqui tamanho é o idTamanho
        quantidade = request.form['quantidade']

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Verifique se a etiqueta existe na tabela Produto
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Produto
                WHERE etiqueta = ?
                """,
                (etiqueta,)
            )
            if cursor.fetchone()[0] == 0:
                return render_template('atualizar_estoque.html', error="Etiqueta do produto não encontrada. Verifique os dados inseridos.", tamanhos=tamanhos)

            # Atualize o estoque (se já existir a etiqueta e o tamanho)
            cursor.execute(
                """
                UPDATE Estoque
                SET quantidade = quantidade + ?
                WHERE etiqueta = ? AND idTamanho = ?
                """,
                (quantidade, etiqueta, tamanho)
            )
            if cursor.rowcount == 0:  # Caso não tenha encontrado o registro para atualizar, insira um novo
                cursor.execute(
                    """
                    INSERT INTO Estoque (etiqueta, idTamanho, quantidade)
                    VALUES (?, ?, ?)
                    """,
                    (etiqueta, tamanho, quantidade)
                )
            # Commit da transação
            conn.commit()
        except Exception as e:
            return render_template('atualizar_estoque.html', error=str(e), tamanhos=tamanhos)
        finally:
            conn.close()

        # Passa a mensagem de sucesso para o template
        return render_template('atualizar_estoque.html', success="Estoque atualizado com sucesso!", tamanhos=tamanhos)

    # Caso a requisição seja GET, passa os tamanhos para o template
    return render_template('atualizar_estoque.html', tamanhos=tamanhos)


def obter_tamanhos():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Use o nome correto da coluna: nome_Tamanho
        cursor.execute("SELECT idTamanho, nome_Tamanho FROM Tamanho")
        tamanhos = cursor.fetchall()
    finally:
        conn.close()
    # Retorne um dicionário com as colunas certas
    return [{"idTamanho": row[0], "nome_Tamanho": row[1]} for row in tamanhos]

@app.route('/gerenciar_categorias_atributos', methods=['GET', 'POST'])
def gerenciar_categorias_atributos():
    conn = connect_db()
    cursor = conn.cursor()

    success_message = None  # Variável para mensagem de sucesso
    error_message = None    # Variável para mensagem de erro

    if request.method == 'POST':
        # Identificar o formulário enviado e realizar o INSERT correspondente
        categoria = request.form.get('categoria')
        subcategoria = request.form.get('subcategoria')
        modelo = request.form.get('modelo')
        marca = request.form.get('marca')
        cor = request.form.get('cor')
        tamanho = request.form.get('tamanho')
        estampa = request.form.get('estampa')
        categoria_id = request.form.get('categoria_id')  # Para Subcategoria

        try:
            if categoria:
                cursor.execute("INSERT INTO Categoria (nome_Categoria) VALUES (?)", (categoria,))
                success_message = "Categoria cadastrada com sucesso!"
            elif subcategoria and categoria_id:
                cursor.execute("INSERT INTO SubCategoria (nome_SubCategoria, idCategoria) VALUES (?, ?)", 
                               (subcategoria, categoria_id))
                success_message = "Subcategoria cadastrada com sucesso!"
            elif modelo:
                cursor.execute("INSERT INTO Modelo (nome_Modelo) VALUES (?)", (modelo,))
                success_message = "Modelo cadastrado com sucesso!"
            elif marca:
                cursor.execute("INSERT INTO Marca (nome_Marca) VALUES (?)", (marca,))
                success_message = "Marca cadastrada com sucesso!"
            elif cor:
                cursor.execute("INSERT INTO Cor (nome_Cor) VALUES (?)", (cor,))
                success_message = "Cor cadastrada com sucesso!"
            elif tamanho:
                cursor.execute("INSERT INTO Tamanho (nome_Tamanho) VALUES (?)", (tamanho,))
                success_message = "Tamanho cadastrado com sucesso!"
            elif estampa:
                cursor.execute("INSERT INTO Estampa (tipo_Estampa) VALUES (?)", (estampa,))
                success_message = "Estampa cadastrada com sucesso!"
            else:
                error_message = "Preencha todos os campos corretamente."

            conn.commit()
        except Exception as e:
            conn.rollback()
            error_message = f"Ocorreu um erro: {str(e)}"
        finally:
            conn.close()

    # Carregar categorias para o formulário de Subcategoria
    conn = connect_db()  # Reconectar para carregar dados
    cursor = conn.cursor()
    cursor.execute("SELECT idCategoria, nome_Categoria FROM Categoria")
    categorias = cursor.fetchall()
    conn.close()

    return render_template(
        'gerenciar_categorias_atributos.html', 
        categorias=categorias,
        success=success_message,
        error=error_message
    )

@app.route('/visualizar_etiquetas', methods=['GET'])
def visualizar_etiquetas():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = """
            SELECT P.etiqueta, 
                   C.nome_Categoria AS categoria, 
                   S.nome_SubCategoria AS subcategoria, 
                   M.nome_Modelo AS modelo, 
                   Marca.nome_Marca AS marca, 
                   Cor.nome_Cor AS cor, 
                   Est.tipo_Estampa AS estampa, 
                   P.preco_unitario
            FROM Produto P
            JOIN Categoria C ON P.idCategoria = C.idCategoria
            JOIN SubCategoria S ON P.idSubCategoria = S.idSubCategoria
            JOIN Modelo M ON P.idModelo = M.idModelo
            JOIN Marca ON P.idMarca = Marca.idMarca
            JOIN Cor ON P.idCor = Cor.idCor
            JOIN Estampa Est ON P.idEstampa = Est.idEstampa
            ORDER BY categoria DESC
        """
        cursor.execute(query)
        etiquetas = cursor.fetchall()
        conn.close()
        return render_template('visualizar_etiquetas.html', etiquetas=etiquetas)
    except Exception as e:
        conn.close()
        return render_template('visualizar_etiquetas.html', error=str(e))


# ========================
# GERENCIAR VENDAS
# ========================

@app.route('/realizar_venda', methods=['GET', 'POST'])
def realizar_venda():
    conn = connect_db()
    cursor = conn.cursor()

    # Obter tamanhos para exibir no HTML
    cursor.execute("SELECT idTamanho, nome_tamanho FROM Tamanho")
    tamanhos = cursor.fetchall()

    # Buscar todos os funcionários
    cursor.execute("""
        SELECT f.idFuncionario, p.nome
        FROM Funcionario f
        JOIN Pessoa p ON f.idPessoa = p.idPessoa
    """)
    vendedores = cursor.fetchall()

    # Obter tipos de pagamento
    cursor.execute("SELECT idTipoPag, Tipo FROM TipoPagamento")
    tipos_pagamento = cursor.fetchall()

    if request.method == 'POST':
        cpf_cliente = request.form.get('cpf_cliente')
        sem_cpf = request.form.get('sem_cpf')  # Checkbox para consumidor padrão
        tipo_pagamento = request.form['tipo_pagamento']
        vendedor_id = request.form['vendedor']  # Vendedor selecionado no formulário

        total = 0
        produtos = []
        
        # Processar os produtos enviados no formulário
        for i in range(len(request.form.getlist('etiqueta'))):
            etiqueta = request.form.getlist('etiqueta')[i]
            tamanho = request.form.getlist('tamanho')[i]
            quantidade = int(request.form.getlist('quantidade')[i])

            # Buscar o preco_unitario e estoque disponível na tabela Produto com base na etiqueta
            cursor.execute("""
                SELECT preco_unitario, quantidade FROM Produto
                JOIN Estoque ON Produto.etiqueta = Estoque.etiqueta
                WHERE Produto.etiqueta = ?
            """, (etiqueta,))
            produto_result = cursor.fetchone()

            if produto_result:
                preco_unitario, estoque_disponivel = produto_result
                # Verificar se há estoque suficiente
                if quantidade > estoque_disponivel:
                    flash(f"Estoque insuficiente para o produto {etiqueta}!", "danger")
                    conn.rollback()  # Reverte todas as alterações feitas até aqui
                    return redirect(url_for('realizar_venda'))

                # Calcular o total do produto
                total_produto = preco_unitario * quantidade
                total += total_produto

                # Adicionar o produto à lista
                produtos.append({
                    'etiqueta': etiqueta,
                    'tamanho': tamanho,
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                    'total_produto': total_produto
                })
            else:
                flash(f"Produto com etiqueta {etiqueta} não encontrado!", "danger")
                conn.rollback()
                return redirect(url_for('realizar_venda'))

        # Verificar se "Consumidor" foi marcado
        if sem_cpf:
            id_cliente = 1  # ID fixo para o consumidor padrão
        else:
            # Buscar cliente pelo CPF na tabela Pessoa
            cursor.execute("""
                SELECT c.idCliente FROM Cliente c
                JOIN Pessoa p ON c.idPessoa = p.idPessoa
                WHERE p.cpf = ?
            """, (cpf_cliente,))
            cliente_result = cursor.fetchone()

            if cliente_result:
                id_cliente = cliente_result[0]  # idCliente retornado da tabela Cliente
            else:
                id_cliente = None  # Caso não encontre cliente

        # Inserir a venda na tabela Venda
        cursor.execute("""
            INSERT INTO Venda (idCliente, idTipoPag, valor_total, idFuncionario) 
            VALUES (?, ?, ?, ?)
        """, (id_cliente, tipo_pagamento, total, vendedor_id))
        conn.commit()

        # Obter o idVenda da venda recém-inserida usando SCOPE_IDENTITY()
        cursor.execute("SELECT SCOPE_IDENTITY()")
        id_venda = cursor.fetchone()[0]

        # Inserir os produtos na tabela ItemVenda e atualizar estoque
        for produto in produtos:
            cursor.execute("""
                INSERT INTO ItemVenda (idVenda, etiqueta, idTamanho, quantidade) 
                VALUES (?, ?, ?, ?)
            """, (id_venda, produto['etiqueta'], produto['tamanho'], produto['quantidade']))

            # Atualizar o estoque, decrementando a quantidade
            cursor.execute("""
                UPDATE Estoque SET quantidade = quantidade - ? WHERE etiqueta = ?
            """, (produto['quantidade'], produto['etiqueta']))

        conn.commit()

        return render_template('realizar_venda.html', success="Venda realizada com sucesso!", vendedores=vendedores, tamanhos=tamanhos, tipos_pagamento=tipos_pagamento)

    return render_template('realizar_venda.html', vendedores=vendedores, tamanhos=tamanhos, tipos_pagamento=tipos_pagamento)


@app.route('/consultar_vendas')
def consultar_vendas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VENDAS_SIMPLES")
    vendas = cursor.fetchall()
    conn.close()
    return render_template('consultar_vendas.html', vendas=vendas)

# ========================
# GERENCIAR CLIENTES
# ========================

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        sexo = request.form['sexo']
        data_nascimento = request.form['data_nascimento']
        telefone = request.form['telefone']
        email = request.form['email']

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                EXEC PROC_INSERIR_CLIENTE ?, ?, ?, ?, ?, ?
                """,
                (nome, cpf, sexo, data_nascimento, telefone, email)
            )
            conn.commit()
        except Exception as e:
            return render_template('cadastrar_cliente.html', error=str(e))
        finally:
            conn.close()
        return redirect(url_for('visualizar_clientes'))
    return render_template('cadastrar_cliente.html')

@app.route('/visualizar_clientes')
def visualizar_clientes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT P.nome, P.CPF, P.email, C.data_Cadastro, 
               (SELECT COUNT(*) FROM Venda WHERE Venda.idCliente = C.idCliente) AS quantidade_compras
        FROM Cliente C
        JOIN Pessoa P ON C.idPessoa = P.idPessoa
        """
    )
    clientes = cursor.fetchall()
    conn.close()
    return render_template('visualizar_clientes.html', clientes=clientes)

@app.route('/gerenciar_setor')
def gerenciar_setor():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Consulta para obter os setores e a quantidade de funcionários
    cursor.execute("""
        SELECT 
            S.nome_Setor, 
            COUNT(F.idFuncionario) AS Quantidade_Funcionarios
        FROM 
            SETOR S
        LEFT JOIN 
            FUNCIONARIO F ON S.idSetor = F.idSetor
        GROUP BY 
            S.nome_Setor;
    """)
    setores = cursor.fetchall()
    conn.close()
    
    return render_template('gerenciar_setor.html', setores=setores)

@app.route('/cadastrar_setor', methods=['GET', 'POST'])
def cadastrar_setor():
    if request.method == 'POST':
        nome_setor = request.form['nome_Setor']
        
        conn = connect_db()
        cursor = conn.cursor()
        
        # Inserir o novo setor no banco de dados
        cursor.execute("INSERT INTO SETOR (nome_Setor) VALUES (?)", (nome_setor,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('gerenciar_setor'))
    
    return render_template('cadastrar_setor.html')


# ========================
# RODANDO O SERVIDOR
# ========================

if __name__ == '__main__':
    threading.Thread(target=lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(debug=True, use_reloader=False)

