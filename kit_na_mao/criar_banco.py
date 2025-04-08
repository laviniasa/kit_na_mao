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

# Salvar e fechar a conexão
conn.commit()
conn.close()

print("Banco de dados e tabela criados com sucesso!")
