-- Tabela Auxiliares
CREATE TABLE CATEGORIA(
idCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_Categoria NVARCHAR(25) NOT NULL
)


CREATE TABLE SUBCATEGORIA(
idSubCategoria INT PRIMARY KEY IDENTITY(1,1),
nome_SubCategoria NVARCHAR(25) NOT NULL,
idCategoria INT not null
CONSTRAINT FK_CATEGORIA_SUB FOREIGN KEY (idCategoria)
REFERENCES CATEGORIA (idCategoria)
)


CREATE TABLE Modelo (
idModelo INT PRIMARY KEY IDENTITY(1,1),
nome_Modelo NVARCHAR(30) NOT NULL
)


CREATE TABLE Marca (
idMarca INT PRIMARY KEY IDENTITY(1,1),
nome_Marca VARCHAR(20) NOT NULL
)

CREATE TABLE Cor (
idCor INT PRIMARY KEY IDENTITY(1,1),
nome_Cor VARCHAR(20) NOT NULL
)

CREATE TABLE Tamanho (
idTamanho INT PRIMARY KEY IDENTITY(1,1),
nome_Tamanho VARCHAR(5) NOT NULL,
idCategoria INT not null,
CONSTRAINT FK_TAMANHO_SUB FOREIGN KEY (idCategoria)
REFERENCES CATEGORIA (idCategoria)
)

CREATE TABLE Estampa (
idEstampa INT PRIMARY KEY IDENTITY(1,1),
tipo_Estampa VARCHAR(50) NOT NULL
)

-- Tabelas Principas (Produto, Estoque, Venda, ItemVenda, Pessoa, Cliente, Funcionário, Setor_Func e Usuarios)
CREATE TABLE PESSOA(
idPessoa INT PRIMARY KEY IDENTITY(1,1),
Nome NVARCHAR(100) NOT NULL,
CPF VARCHAR(11) UNIQUE NOT NULL,
Sexo VARCHAR(1) NOT NULL,
data_Nascimento DATE NOT NULL,
Telefone VARCHAR(15) NOT NULL,
Email NVARCHAR(50) NOT NULL
)

CREATE TABLE CLIENTE(
idCliente INT PRIMARY KEY IDENTITY(1,1),
data_Cadastro DATE DEFAULT GETDATE(),
idPessoa INT NOT NULL
)

CREATE TABLE SETOR(
idSetor INT PRIMARY KEY IDENTITY(1,1),
nome_Setor VARCHAR(20))


CREATE TABLE FUNCIONARIO(
idFuncionario INT PRIMARY KEY IDENTITY(1,1),
idPessoa INT NOT NULL FOREIGN KEY REFERENCES PESSOA (idPessoa),
idSetor INT NOT NULL FOREIGN KEY REFERENCES SETOR (idSetor),
Data_Adimissao DATE DEFAULT GETDATE(),
Salario DECIMAL(9,2)
)


CREATE TABLE Produto (
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


CREATE TABLE Estoque (
etiqueta VARCHAR(40),
quantidade INT NOT NULL
CONSTRAINT FK_ESTOQUE_PRODUTO FOREIGN KEY (etiqueta)
REFERENCES Produto(etiqueta)
)


CREATE TABLE Venda (
idVenda INT PRIMARY KEY IDENTITY(1,1),
valor_total DECIMAL(10, 2) NOT NULL,
data_venda DATETIME DEFAULT GETDATE(),
idCliente INT NOT NULL,
idFuncionario INT NOT NULL
)

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