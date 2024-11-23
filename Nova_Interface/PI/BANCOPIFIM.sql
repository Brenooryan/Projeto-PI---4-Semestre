-- Tabela Auxiliares

-- Tabela Categoria EX:( Roupas, Calçados e Acessórios)
CREATE TABLE CATEGORIA(
idCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_Categoria NVARCHAR(25) NOT NULL
)

-- Tabela SUBCATEGORIA EX:( Camisa, short, agasalho, tenis, chinelo, boné, corrente)
CREATE TABLE SUBCATEGORIA(
idSubCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_SubCategoria NVARCHAR(25) NOT NULL,
idCategoria INT not null
CONSTRAINT FK_CATEGORIA_SUB FOREIGN KEY (idCategoria)
REFERENCES CATEGORIA (idCategoria)
)

-- Tabela Modelo EX:(Manga curta, manga longa, Moletom, corta vento)
CREATE TABLE MODELO (
idModelo INT PRIMARY KEY IDENTITY(1,1),
nome_Modelo NVARCHAR(30) NOT NULL
)

--Tabela Marca EX:(Nike, Adidas, Puma)
CREATE TABLE MARCA (
idMarca INT PRIMARY KEY IDENTITY(1,1),
nome_Marca VARCHAR(20) NOT NULL
)

--Tabela Cor EX:(Azul, preto, branco)
CREATE TABLE COR (
idCor INT PRIMARY KEY IDENTITY(1,1),
nome_Cor VARCHAR(20) NOT NULL
)

--Tabela Tamnaho EX:(42,44, G, GG)
CREATE TABLE TAMANHO (
idTamanho INT PRIMARY KEY IDENTITY(1,1),
nome_Tamanho VARCHAR(5) NOT NULL
)

--Tabela Estampa EX:(Sem estampa, Estampa pequena na frente, Estampa pequena na frnete e Grande nas costas)
CREATE TABLE ESTAMPA (
idEstampa INT PRIMARY KEY IDENTITY(1,1),
tipo_Estampa VARCHAR(50) NOT NULL
)

-- Tabelas Principas (Produto, Estoque, Venda, ItemVenda, Pessoa, Cliente, Funcionário, Setor_Func e Usuarios)

--Tabela Pessoa (Para ter as informações tanto de funcionário quanto de Cliente)
CREATE TABLE PESSOA(
idPessoa INT PRIMARY KEY IDENTITY(1,1),
Nome NVARCHAR(100) NOT NULL,
CPF VARCHAR(11) UNIQUE NOT NULL,
Sexo VARCHAR(1) NOT NULL,
data_Nascimento DATE NOT NULL,
Telefone VARCHAR(15) NOT NULL,
Email NVARCHAR(50) NOT NULL
)

--Tabela Cliente (Pega as informações da tabela pessoa e serve para ter o registro do comprador)
CREATE TABLE CLIENTE(
idCliente INT PRIMARY KEY IDENTITY(1,1),
data_Cadastro DATE DEFAULT GETDATE(),
idPessoa INT NOT NULL
)

--Tabela Setor (Serve para definir os setores da loja Ex: Gerencia, Vendas e RH, com isso ao cadastrar um funcionario defini o setor dele)
CREATE TABLE SETOR(
idSetor INT PRIMARY KEY IDENTITY(1,1),
nome_Setor VARCHAR(20)
)

--Tabela Funcionario( Vai pegar as informaçoes da tabela pessoa, alocar a um setor e registrar a data de adimissão e o salario, 
--dando a possibilidade também de saber quem realizou a venda)
CREATE TABLE FUNCIONARIO(
idFuncionario INT PRIMARY KEY IDENTITY(1,1),
idPessoa INT NOT NULL FOREIGN KEY REFERENCES PESSOA (idPessoa),
idSetor INT NOT NULL FOREIGN KEY REFERENCES SETOR (idSetor),
Data_Adimissao DATE DEFAULT GETDATE(),
Salario DECIMAL(9,2)
)

--Tabela Produto (Onde vai cadastrar os produtos pegando as informações das auxiliares, alem disso usando a etiqueta dele e 
--definindo seu preço)
CREATE TABLE PRODUTO (
etiqueta VARCHAR(40) PRIMARY KEY NOT NULL,
idCategoria INT not null,
idSubCategoria INT NOT NULL,
idModelo INT NOT NULL,
idMarca INT NOT NULL,
idCor INT NOT NULL,
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
CONSTRAINT FK_Produto_Estampa FOREIGN KEY (idEstampa) 
REFERENCES Estampa(idEstampa)
)

--Tabela Estoque (Onde vai ter o controle da quantidade dos produtos)
CREATE TABLE ESTOQUE (
etiqueta VARCHAR(40),
quantidade INT NOT NULL,
idTamanho INT NOT NULL,
CONSTRAINT FK_ESTOQUE_PRODUTO FOREIGN KEY (etiqueta)
REFERENCES Produto(etiqueta),
CONSTRAINT FK_ESTOQUE_TAMANHO FOREIGN KEY (idTamanho)
REFERENCES TAMANHO(idTamanho)
)

--Tabela Tipo de Pagamento Ex:(Pix, Dinheiro, Cartão)
CREATE TABLE TipoPagamento(
idTipoPag INT PRIMARY KEY IDENTITY(1,1),
Tipo VARCHAR(18) NOT NULL)

--Tabela Venda (onde vai ser armazenado as infos da venda como valor total, data, cliente, vendedor e tipo de pagamento)
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

--Tabela ItemVenda(onde funciona como carrinho, serve para poder vender mais de um produto em uma unica venda)
CREATE TABLE ItemVenda (
idItemVenda INT PRIMARY KEY IDENTITY(1,1),
idVenda INT NOT NULL,
etiqueta VARCHAR(40) NOT NULL,
quantidade INT NOT NULL,
idTamanho INT NOT NULL,
CONSTRAINT FK_ItemVenda_Venda FOREIGN KEY (idVenda) 
REFERENCES Venda(idVenda),
CONSTRAINT FK_ItemVenda_Produto FOREIGN KEY (etiqueta) 
REFERENCES Produto(etiqueta),
CONSTRAINT FK_ItemVenda_Tamanho FOREIGN KEY (idTamanho)
REFERENCES TAMANHO(idTamanho)
)

--Tabela Usuario (serve para armazenar os usuarios da interface, e armazena quem é o dono desse usuario também)
CREATE TABLE USUARIO (
idUsuario INT PRIMARY KEY IDENTITY(1,1),
username NVARCHAR(20) NOT NULL,
senha NVARCHAR(20) NOT NULL,
idFuncionario int not null
CONSTRAINT FK_USUARIO_FUNC FOREIGN KEY (idFuncionario)
REFERENCES FUNCIONARIO(idFuncionario)
)

CREATE TABLE STATUS_FUNCIONARIO(
idFuncionario int not null,
statusFunc varchar(15),
dataStatus DATETIME DEFAULT GETDATE()
constraint fk_status_func foreign key (idFuncionario)
references FUNCIONARIO (idFuncionario),
CONSTRAINT CHK_sts CHECK (statusFunc IN ('Ativo', 'Demitido', 'Readmitido') ))

--Tipo de Pagamento:
INSERT INTO TipoPagamento (Tipo) 
VALUES ('PIX'), ('Dinheiro'), ('Cartão de Crédito'), ('Cartão de Débito')

--Setor:
INSERT INTO SETOR (nome_Setor) 
VALUES ('Gerencia'), ('Vendas'), ('RH')

INSERT INTO CATEGORIA (nome_Categoria) 
VALUES ('Roupas'), ('Calçados'), ('Acessórios')

INSERT INTO SUBCATEGORIA (nome_SubCategoria,idCategoria) 
VALUES 
('Camisa',1),
('Agasalho',1),
('Jaqueta',1),
('Bermuda',1),
('Short',1),
('Calça',1),
('Corrente',3),
('Tênis',2),
('Chinelo',2),
('Boné',3),
('Sapato',2);

INSERT INTO Modelo (nome_Modelo) 
VALUES 
('Manga Curta'),
('Manga Longa'),
('Regata'),
('Polo'),
('Moletom com Capuz'),
('Moletom sem Capuz'),
('Sarja'),
('Moletom'),
('Jeans'),
('Couro'),
('Ouro'),
('Corrida'),
('Casual'),
('Plataforma'),
('Sapatênis'),
('Dunk'),
('Prata'),
('Dedo'),
('Nuvem'),
('Slide');


INSERT INTO Cor (Nome_cor) 
VALUES 
('Preto'),
('Branco'),
('Cinza'),
('Azul Marinho'),
('Azul Claro'),
('Vermelho'),
('Verde'),
('Bege'),
('Marrom'),
('Roxo'),
('Laranja'),
('Amarelo'),
('Escuro'),
('Sem cor'),
('Claro');


INSERT INTO Marca (Nome_marca) 
VALUES 
('Nike'),
('Adidas'),
('Puma'),
('Oakley'),
('Lacoste'),
('Calvin Klein'),
('Tommy Hilfiger'),
('Reserva'),
('Hurley'),
('Quiksilver'),
('Element'),
('Vans'),
('Sem Marca'),
('Havaianas'),
('Kenner');


INSERT INTO Estampa (tipo_estampa) 
VALUES 
('Sem estampa'),
('Estampa pequena na frente'),
('Estampa grande nas costas'),
('Estampa pequena na frente e grande atrás'),
('Estampa grande na frente');


INSERT INTO Tamanho (nome_Tamanho) 
VALUES 
('PP'),
('P'),
('M'),
('G'),
('GG'),
('XG'),
('XGG'),
('33'),
('34'),
('35'),
('36'),
('37'),
('38'),
('39'),
('40'),
('41'),
('42'),
('43'),
('44'),
('Único');

INSERT INTO PESSOA(Nome,CPF,Sexo,data_Nascimento,Telefone,Email)
VALUES('JOÃO','123456','M','20/08/2004','12347168','J@GMAIL.COM')

INSERT INTO FUNCIONARIO(idPessoa, idSetor,Salario)
VALUES(1,1,5000)

insert into USUARIO(USERNAME,SENHA,IDFUNCIONARIO)
VALUES('TESTE','12',1)

CREATE PROCEDURE InserirProduto
    @etiqueta NVARCHAR(100),
    @idCategoria INT,
    @idSubCategoria INT,
    @idModelo INT,
    @idMarca INT,
    @idCor INT,
    @idEstampa INT,
    @preco DECIMAL(10, 2)
AS
BEGIN
    -- Verifica se a subcategoria pertence à categoria
    IF EXISTS (SELECT 1 FROM SubCategoria WHERE idCategoria = @idCategoria AND idSubCategoria = @idSubCategoria)
    BEGIN
        -- Insere o produto
        INSERT INTO Produto (etiqueta, idCategoria, idSubCategoria, idModelo, idMarca, idCor, idEstampa, preco_unitario)
        VALUES (@etiqueta, @idCategoria, @idSubCategoria, @idModelo, @idMarca, @idCor, @idEstampa, @preco)
    END
    ELSE
    BEGIN
        -- Se a subcategoria não pertence à categoria, gera um erro
        RAISERROR('A subcategoria não corresponde à categoria selecionada.', 16, 1);
    END
END

CREATE TRIGGER trg_after_insert_funcionario
ON FUNCIONARIO
AFTER INSERT
AS
BEGIN
    INSERT INTO STATUS_FUNCIONARIO (idFuncionario, statusFunc, dataStatus)
    SELECT idFuncionario, 'Ativo', GETDATE()
    FROM inserted;
END;