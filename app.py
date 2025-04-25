from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from flask import send_from_directory
from werkzeug.utils import secure_filename
import uuid
from flask import flash


# Criação da instância da aplicação Flask
app = Flask(__name__)


# Configuração de uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Conectar ao banco de dados SQLite
DB_PATH = "banco.db"

app.secret_key = 'chave_secreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Criar banco de dados SQLite
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Excluir a tabela antigos e recriar a nova
        cursor.execute('''DROP TABLE IF EXISTS novos_cadastros''')

        # Criar a tabela com a nova coluna 'email'
        cursor.execute('''CREATE TABLE IF NOT EXISTS novos_cadastros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            corrida_nome TEXT NOT NULL,
                            comprovante TEXT NOT NULL,
                            documento TEXT NOT NULL,
                            email TEXT)''')  # Agora com a coluna email

        # Criar as outras tabelas se necessário
        cursor.execute('''CREATE TABLE IF NOT EXISTS cadastros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            email TEXT NOT NULL,
                            corrida TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS corridas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS inscricoes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            email TEXT NOT NULL,
                            corrida_id INTEGER,
                            FOREIGN KEY (corrida_id) REFERENCES corridas(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS imagens_carrossel (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            imagem TEXT NOT NULL,
                            corrida_nome TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS carrossel (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome_arquivo TEXT NOT NULL,
                            corrida_nome TEXT NOT NULL)''')

# Chamar a função para criar as tabelas
init_db()

# Usuários permitidos
USUARIOS = {
    "laviniasaadm": "zaq12wsx#",
    "anacarolinaadm": "kitnamao_12345"
}

@app.route('/')
def index():
    # Conectando-se ao banco para buscar cadastros
    cadastros = obter_cadastros_do_banco()
    print(cadastros)  # Verifique o que está sendo retornado

    # Buscar imagens para o carrossel
    caminho_carrossel = os.path.join('static', 'img')
    os.makedirs(caminho_carrossel, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT imagem, corrida_nome FROM imagens_carrossel')
    imagens_carrossel = cursor.fetchall()
    conn.close()

    # Passando as imagens e cadastros para o template
    return render_template('index.html', cadastros=cadastros, imagens_carrossel=imagens_carrossel)



def obter_cadastros_do_banco():
    # Conectando-se ao banco de dados
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    # Executa a consulta para buscar os cadastros
    cursor.execute('SELECT * FROM cadastros')
    dados = cursor.fetchall()
    
    # Fecha a conexão com o banco de dados
    conn.close()
    
    return dados

@app.route('/index.html')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario in USUARIOS and USUARIOS[usuario] == senha:
        session['usuario'] = usuario
        return redirect(url_for('admin'))
    return "Usuário ou senha incorretos!", 403

@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form.get('nome')
    corrida_nome = request.form.get('corrida_nome')  # Pega o nome da corrida do campo oculto
    email = request.form.get('email')  # Captura o e-mail

    # Verificação dos dados
    if not nome or not corrida_nome or not email:
        return "Erro: Todos os campos são obrigatórios!", 400

    # Verifica se os arquivos foram enviados corretamente
    comprovante = request.files.get('comprovante')
    documento = request.files.get('documento')

    if not comprovante or not documento:
        return "Erro: Comprovante e documento são obrigatórios!", 400

    # Caminhos para salvar os arquivos
    comprovante_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(comprovante.filename))
    documento_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(documento.filename))

    # Salvar os arquivos
    comprovante.save(comprovante_path)
    documento.save(documento_path)

    # Salvar no banco de dados, incluindo o e-mail
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO novos_cadastros (nome, corrida_nome, comprovante, documento, email) VALUES (?, ?, ?, ?, ?)",
        (nome, corrida_nome, comprovante.filename, documento.filename, email)  # Incluindo o e-mail
    )
    conn.commit()
    conn.close()

    flash('Seu formulário foi enviado com sucesso! Aguarde a confirmação via Email', 'success')
    return redirect(url_for('index'))

    return redirect(request.referrer)





@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM novos_cadastros")  # Tabela de cadastros
    cadastros = cursor.fetchall()
    conn.close()

    print(f"Cadastros após exclusão: {cadastros}")  # Verifica os cadastros após a exclusão

    # Lista de imagens do carrossel
    imagens_carrossel = []
    img_folder = os.path.join(os.getcwd(), 'static', 'img')

    if os.path.exists(img_folder):  # Verifica se a pasta de imagens existe
        imagens_carrossel = [
            f for f in os.listdir(img_folder)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        ]

    return render_template('adm.html', cadastros=cadastros, imagens_carrossel=imagens_carrossel)





@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/download/<path:filename>')
def baixar_arquivo(filename):
    return send_from_directory(directory="uploads", path=filename, as_attachment=True)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_cadastro(id):
    print(f"Tentando excluir o cadastro com ID: {id}")  # Verifica o ID que foi passado
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "DELETE FROM novos_cadastros WHERE id = ?"
    print(f"Executando a query: {query} com ID: {id}")
    
    cursor.execute(query, (id,))
    
    # Verifique se o comando DELETE afetou alguma linha
    rows_affected = cursor.rowcount
    print(f"Linhas afetadas: {rows_affected}")
    
    conn.commit()
    conn.close()
    
    if rows_affected > 0:
        print(f"Cadastro com ID {id} foi excluído.")
    else:
        print(f"Nenhum cadastro encontrado com ID {id}.")
    
    return redirect(url_for('admin'))




# Rota para adicionar a imagem ao carrossel
@app.route('/upload_carrossel', methods=['POST'])
def upload_carrossel():
    imagem = request.files.get('imagem')
    corrida_nome = request.form['corrida_nome']

    # Verificações básicas
    if not imagem or imagem.filename == '':
        flash("Nenhuma imagem selecionada.")
        return redirect(url_for('mostrar_upload_carrossel'))

    if not imagem.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        flash("Formato inválido.")
        return redirect(url_for('mostrar_upload_carrossel'))

    # Gera um nome único para a imagem
    nome_imagem = str(uuid.uuid4()) + os.path.splitext(imagem.filename)[1]

    # Caminho final de destino para a imagem
    destino = os.path.join('static', 'img', nome_imagem)
    imagem.save(destino)

    # Salva a imagem e o nome da corrida no banco de dados
    salvar_imagem_carrossel(nome_imagem, corrida_nome)

    flash("Imagem adicionada com sucesso!")
    return redirect(url_for('mostrar_upload_carrossel'))


# Rota para mostrar o formulário de upload
@app.route('/upload_carrossel', methods=['GET'])
def mostrar_upload_carrossel():
    imagens = buscar_imagens_carrossel()
    print(imagens)  # DEBUG
    return render_template('adm.html', imagens=imagens)

def buscar_imagens_carrossel():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT imagem FROM imagens_carrossel")
        imagens = cursor.fetchall()
        return [imagem[0] for imagem in imagens]

@app.route('/admin/upload', methods=['POST'])
def upload_carrossel_admin():
    if 'imagem' not in request.files:
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('admin'))

    imagem = request.files['imagem']
    if imagem.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('admin'))

    if imagem:
        caminho = os.path.join('static', 'carrossel', imagem.filename)
        imagem.save(caminho)
        flash('Imagem adicionada com sucesso!')
        return redirect(url_for('admin'))
    
@app.route('/admin/excluir_imagem', methods=['POST'])
def excluir_imagem_carrossel():
    # Pega o nome da imagem da requisição
    nome_imagem = request.form['nome_imagem']

    # Caminho da imagem no diretório
    caminho_imagem = os.path.join(app.static_folder, 'img', nome_imagem)

    # Verifica se a imagem existe no diretório e exclui
    if os.path.exists(caminho_imagem):
        os.remove(caminho_imagem)

    # Exclui o registro correspondente no banco de dados
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM imagens_carrossel WHERE imagem = ?", (nome_imagem,))
    conn.commit()
    conn.close()

    flash('Imagem excluída com sucesso!')
    return redirect(url_for('admin'))



@app.route('/imagem/<int:id>')
def show_image(id):
    caminho_carrossel = os.path.join('static', 'img')
    imagens_carrossel = os.listdir(caminho_carrossel)
    
    # Verifica se a imagem existe pelo índice (id)
    if id < len(imagens_carrossel):
        imagem = imagens_carrossel[id]
        return render_template('show_image.html', imagem=imagem)
    else:
        return "Imagem não encontrada", 404


# Função para obter os dados da corrida pelo ID
def obter_corrida(corrida_id):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM corridas WHERE id = ?', (corrida_id,))
    corrida = cursor.fetchone()  # Retorna uma tupla com os dados da corrida
    conn.close()
    return corrida

# Função para salvar a inscrição no banco de dados
def salvar_inscricao(nome, email, corrida_id):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO inscricoes (nome, email, corrida_id) VALUES (?, ?, ?)', (nome, email, corrida_id))
    conn.commit()
    conn.close()

@app.route('/formulario/<int:corrida_id>', methods=['GET', 'POST'])
def form_cadastro(corrida_id):
    # Busca os dados da corrida no banco de dados
    corrida = obter_corrida(corrida_id)

    if request.method == 'POST':
        # Processa os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        salvar_inscricao(nome, email, corrida_id)  # Salva a inscrição no banco
        return redirect(url_for('confirmacao'))  # Redireciona para uma página de confirmação

    return render_template('formulario.html', corrida=corrida)

@app.route('/confirmacao')
def confirmacao():
    return "Inscrição realizada com sucesso!"

# Função para salvar a imagem no banco de dados com o nome da corrida
def salvar_imagem_carrossel(imagem_filename, corrida_nome):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO imagens_carrossel (imagem, corrida_nome)
        VALUES (?, ?)
    ''', (imagem_filename, corrida_nome))
    conn.commit()
    conn.close()


@app.route('/upload_carrossel/<int:id_corrida>')
def mostrar_upload_carrossel_por_corrida(id_corrida):
    # Aqui, você deve buscar as informações da corrida no banco de dados
    corrida = obter_corrida(corrida_id=id_corrida)  # Função para buscar a corrida
    return render_template('upload_carrossel.html', corrida=corrida)

@app.route('/inscricao', methods=['POST'])
def inscricao():
    corrida_id = request.form['corrida_id']
    nome = request.form['nome']
    email = request.form['email']

    # Salve as informações no banco de dados
    salvar_inscricao(nome, email, corrida_id)
    
    # Opcional: você pode redirecionar ou mostrar uma mensagem de sucesso
    return redirect(url_for('index'))  # Volta para a página inicial



if __name__ == '__main__':
    app.run(debug=True)
