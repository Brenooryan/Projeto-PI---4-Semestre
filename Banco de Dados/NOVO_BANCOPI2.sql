-- Tabela Categoria EX:(Roupas, Calçados e Acessórios)
CREATE TABLE CATEGORIA(
idCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_Categoria NVARCHAR(25) NOT NULL
)

-- Tabela SUBCATEGORIA EX:(Camisa, Short, Agasalho, Tenis, Chinelo,
--Bone e Corrente)
CREATE TABLE SUBCATEGORIA(
idSubCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_SubCategoria NVARCHAR(25) NOT NULL,
idCategoria INT not null
CONSTRAINT FK_CATEGORIA_SUB FOREIGN KEY (idCategoria)
REFERENCES CATEGORIA (idCategoria)
)

-- Tabela Modelo EX:(Manga Curta, Manga Longa, Moletom e Corta-vento)
CREATE TABLE MODELO (
idModelo INT PRIMARY KEY IDENTITY(1,1),
nome_Modelo NVARCHAR(30) NOT NULL
)

--Tabela Marca EX:(Nike, Adidas e Puma)
CREATE TABLE MARCA (
idMarca INT PRIMARY KEY IDENTITY(1,1),
nome_Marca VARCHAR(20) NOT NULL
)

--Tabela Cor EX:(Azul, Preto e Branco)
CREATE TABLE COR (
idCor INT PRIMARY KEY IDENTITY(1,1),
nome_Cor VARCHAR(20) NOT NULL
)

--Tabela Tamanho EX:(42, 44, G, GG)
CREATE TABLE TAMANHO (
idTamanho INT PRIMARY KEY IDENTITY(1,1),
nome_Tamanho VARCHAR(5) NOT NULL,
idCategoria INT not null,
CONSTRAINT FK_TAMANHO_SUB FOREIGN KEY (idCategoria)
REFERENCES CATEGORIA (idCategoria)
)

--Tabela Estampa EX:(Sem estampa, Estampa pequena na frente e
--Estampa pequena na frente e Grande nas costas)
CREATE TABLE ESTAMPA (
idEstampa INT PRIMARY KEY IDENTITY(1,1),
tipo_Estampa VARCHAR(50) NOT NULL
)

-- Tabelas Principas (Produto, Estoque, Venda, ItemVenda, Pessoa, Cliente,
--Funcionário, Setor_Func e Usuarios)

--Tabela Pessoa (Para ter as informações tanto de Funcionário quanto de
--Cliente)
CREATE TABLE PESSOA(
idPessoa INT PRIMARY KEY IDENTITY(1,1),
Nome NVARCHAR(100) NOT NULL,
CPF VARCHAR(11) UNIQUE NOT NULL,
Sexo VARCHAR(1) NOT NULL,
data_Nascimento DATE NOT NULL,
Telefone VARCHAR(15) NOT NULL,
Email NVARCHAR(50) NOT NULL
)

--Tabela Cliente (Guarda as informações da tabela Pessoa 
-- e serve para ter o registro do comprador)
CREATE TABLE CLIENTE(
idCliente INT PRIMARY KEY IDENTITY(1,1),
data_Cadastro DATE DEFAULT GETDATE(),
idPessoa INT NOT NULL
)

--Tabela Setor (Serve para definir os setores da loja Ex: Gerencia, Vendas e RH,
--com isso ao cadastrar um funcionario se define o setor dele)
CREATE TABLE SETOR(
idSetor INT PRIMARY KEY IDENTITY(1,1),
nome_Setor VARCHAR(20)
)

--Tabela Funcionario(Guarda as informaçoes da tabela Pessoa, aloca a um setor,
-- registra a data de admissão e o salário, possibilitando saber quem
-- realizou a venda)
CREATE TABLE FUNCIONARIO(
idFuncionario INT PRIMARY KEY IDENTITY(1,1),
idPessoa INT NOT NULL FOREIGN KEY REFERENCES PESSOA (idPessoa),
idSetor INT NOT NULL FOREIGN KEY REFERENCES SETOR (idSetor),
Data_Adimissao DATE DEFAULT GETDATE(),
Salario DECIMAL(9,2)
)

--Tabela Produto (Para o cadastro de produtos e suas categorias, usando
--a etiqueta dele e definindo seu preço)
CREATE TABLE PRODUTO (
etiqueta VARCHAR(40) PRIMARY KEY NOT NULL,
idCategoria INT not null,
idSubCategoria INT NOT NULL,
idModelo INT NOT NULL,
idMarca INT NOT NULL,
idCor INT NOT NULL,
idTamanho INT,
idEstampa INT NOT NULL,
preco_unitario DECIMAL(10, 2) NOT NULL,   
CONSTRAINT FK_Produto_Categoria FOREIGN KEY (idCategoria) 
REFERENCES Categoria(idCategoria),
CONSTRAINT FK_Produto_SubCategoria FOREIGN KEY (idSubCategoria) 
REFERENCES SubCategoria(idSubCategoria),
CONSTRAINT FK_Produto_Modelo FOREIGN KEY (idModelo) 
REFERENCES Modelo(idModelo),
CONSTRAINT FK_Produto_Marca FOREIGN KEY (idMarca) 
REFERENCES Marca(idMarca),
CONSTRAINT FK_Produto_Cor FOREIGN KEY (idCor) 
REFERENCES Cor(idCor),
CONSTRAINT FK_Produto_Tamanho FOREIGN KEY (idTamanho) 
REFERENCES Tamanho(idTamanho),
CONSTRAINT FK_Produto_Estampa FOREIGN KEY (idEstampa) 
REFERENCES Estampa(idEstampa)
)

--Tabela Estoque (Usada para ter o controle da quantidade de produtos)
CREATE TABLE ESTOQUE (
etiqueta VARCHAR(40),
quantidade INT NOT NULL
CONSTRAINT FK_ESTOQUE_PRODUTO FOREIGN KEY (etiqueta)
REFERENCES Produto(etiqueta)
)

--Trigger InsertEstoque(Usado para criar um produto já inserir automaticamente
--a quantidade de estoque 0 nele evitando bugs por valor null)
CREATE TRIGGER trg_InsertEstoque
ON Produto
AFTER INSERT
AS
BEGIN
    -- Inserir na tabela ESTOQUE com quantidade 0 para o novo produto
    INSERT INTO Estoque (etiqueta, quantidade)
    SELECT etiqueta, 0
    FROM inserted;
END;


--Tabela Tipo de Pagamento Ex:(Pix, Dinheiro, Cartão)
CREATE TABLE TipoPagamento(
idTipoPag INT PRIMARY KEY IDENTITY(1,1),
Tipo VARCHAR(18) NOT NULL)

--Inserção das formas de pagamento padrão
INSERT INTO TipoPagamento (Tipo) 
VALUES ('PIX'), ('Dinheiro'), ('Cartão de Crédito'), ('Cartão de Débito')

--Tabela Venda (Armazena as informações da venda como valor total, data, cliente,
--vendedor e tipo de pagamento)
CREATE TABLE VENDA (
idVenda INT PRIMARY KEY IDENTITY(1,1),
valor_total DECIMAL(10, 2) NOT NULL,
data_venda DATETIME DEFAULT GETDATE(),
idCliente INT NOT NULL,
idFuncionario INT NOT NULL,
idTipoPag INT NOT NULL,
CONSTRAINT FK_VENDA_CLI FOREIGN KEY (idCliente)
REFERENCES CLIENTE (idcliente),
CONSTRAINT FK_VENDA_FUNC FOREIGN KEY (idFuncionario)
REFERENCES FUNCIONARIO (idFuncionario),
CONSTRAINT FK_VENDA_TipoPag FOREIGN KEY (idTipoPag)
REFERENCES TipoPagamento (idTipoPag)
)

--Tabela ItemVenda(Funciona como carrinho, possibilita vender mais de um produto em 
--uma única venda)
CREATE TABLE ItemVenda (
idItemVenda INT PRIMARY KEY IDENTITY(1,1),
idVenda INT NOT NULL,
etiqueta VARCHAR(40) NOT NULL,
quantidade INT NOT NULL,
CONSTRAINT FK_ItemVenda_Venda FOREIGN KEY (idVenda) 
REFERENCES Venda(idVenda),
CONSTRAINT FK_ItemVenda_Produto FOREIGN KEY (etiqueta) 
REFERENCES Produto(etiqueta)
)

--Tabela Usuario (Armazena os usuarios e qual o seu cargo)
CREATE TABLE USUARIO (
id INT PRIMARY KEY IDENTITY(1,1),
username NVARCHAR(50) NOT NULL,
senha NVARCHAR(255) NOT NULL,
idFuncionario int not null
CONSTRAINT FK_USUARIO_FUNC FOREIGN KEY (idFuncionario)
REFERENCES FUNCIONARIO(idFuncionario)
)
