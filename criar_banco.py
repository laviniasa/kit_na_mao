import sqlite3

# Conectar ao banco de dados (cria o arquivo se não existir)
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Criar a tabela "cadastros"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cadastros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        comprovante TEXT NOT NULL,
        documento TEXT NOT NULL
    )
''')

# Criar a tabela "corridas"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS corridas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    )
''')

# Criar a tabela "inscricoes"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inscricoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        corrida_id INTEGER,
        FOREIGN KEY (corrida_id) REFERENCES corridas(id)
    )
''')

# Criar a tabela "imagens"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS imagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_imagem TEXT NOT NULL,
        caminho_imagem TEXT NOT NULL,
        corrida_id INTEGER,
        FOREIGN KEY (corrida_id) REFERENCES corridas(id)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS carrossel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_arquivo TEXT NOT NULL,
        corrida_nome TEXT NOT NULL
    ) 
''')

# Salvar e fechar a conexão
conn.commit()
conn.close()

print("Banco de dados e tabelas criados com sucesso!")
