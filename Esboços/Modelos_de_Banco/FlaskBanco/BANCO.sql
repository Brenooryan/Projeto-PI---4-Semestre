-- Tabelas auxiliares (Modelo, Marca, Cor, Tamanho, Estampa)
CREATE TABLE Modelo (
    idModelo INT PRIMARY KEY IDENTITY(1,1),
    nome_Modelo NVARCHAR(100) NOT NULL
);

CREATE TABLE Marca (
    idMarca INT PRIMARY KEY IDENTITY(1,1),
    nome_Marca NVARCHAR(100) NOT NULL
);

CREATE TABLE Cor (
    idCor INT PRIMARY KEY IDENTITY(1,1),
    nome_Cor NVARCHAR(50) NOT NULL
);

CREATE TABLE Tamanho (
    idTamanho INT PRIMARY KEY IDENTITY(1,1),
    tamanho NVARCHAR(10) NOT NULL
);

CREATE TABLE Estampa (
    idEstampa INT PRIMARY KEY IDENTITY(1,1),
    tipo_Estampa NVARCHAR(100) NOT NULL
);


-- Tabela Produto
CREATE TABLE Produto (
    etiqueta NVARCHAR(50) PRIMARY KEY NOT NULL,
    idModelo INT FOREIGN KEY REFERENCES Modelo(idModelo),
    idMarca INT FOREIGN KEY REFERENCES Marca(idMarca),
    idCor INT FOREIGN KEY REFERENCES Cor(idCor),
    idTamanho INT FOREIGN KEY REFERENCES Tamanho(idTamanho),
    idEstampa INT FOREIGN KEY REFERENCES Estampa(idEstampa),
    preco_unitario DECIMAL(10, 2) NOT NULL
);

-- Tabela Estoque
CREATE TABLE Estoque (
    etiqueta NVARCHAR(50) FOREIGN KEY REFERENCES Produto(etiqueta),
    quantidade INT NOT NULL
);

-- Tabela Venda
CREATE TABLE Venda (
    idVenda INT PRIMARY KEY IDENTITY(1,1),
    valor_total DECIMAL(10, 2) NOT NULL,
    data_venda DATETIME DEFAULT GETDATE()
);

-- Tabela ItemVenda
CREATE TABLE ItemVenda (
    idItemVenda INT PRIMARY KEY IDENTITY(1,1),
    idVenda INT FOREIGN KEY REFERENCES Venda(idVenda),
    etiqueta NVARCHAR(50) FOREIGN KEY REFERENCES Produto(etiqueta),
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL
);


INSERT INTO Modelo (nome_Modelo) 
VALUES 
('Camisa Manga Curta'),
('Camisa Manga Longa'),
('Camisa Regata'),
('Camiseta Polo'),
('Moletom com Capuz'),
('Moletom sem Capuz'),
('Jaqueta'),
('Bermuda de Sarja'),
('Short Moletom'),
('Short Jeans'),
('Calça Jeans'),
('Calça Moletom'),
('Tênis'),
('Chinelo');

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
('Sem Marca');


INSERT INTO Estampa (tipo_estampa) 
VALUES 
('Sem estampa'),
('Estampa pequena na frente'),
('Estampa grande nas costas'),
('Estampa pequena na frente e grande atrás'),
('Estampa grande na frente');


INSERT INTO Tamanho (Tamanho) 
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
('44');


select * from produto
select * from Estoque
select * from ItemVenda
select * from Venda
select * from marca


INSERT INTO Marca (Nome_marca) 
VALUES 
('Red Nose'),
('BRENIN')