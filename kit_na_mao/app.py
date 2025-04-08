from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask import flash


app = Flask(__name__)

DB_PATH = "banco.db"

app.secret_key = 'chave_secreta'
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Criar banco de dados SQLite
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cadastros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            comprovante TEXT NOT NULL,
                            documento TEXT NOT NULL)''')
        conn.commit()

init_db()

# Usuários permitidos
USUARIOS = {
    "laviniasaadm": "zaq12wsx#",
    "anacarolinaadm": "kitnamao_12345"
}

@app.route('/')
def index():
    caminho_carrossel = os.path.join('static', 'img')  # ALTERADO
    os.makedirs(caminho_carrossel, exist_ok=True)

    imagens_carrossel = os.listdir(caminho_carrossel)
    cadastros = obter_cadastros_do_banco()
    return render_template('index.html', cadastros=cadastros, imagens_carrossel=imagens_carrossel)


def obter_cadastros_do_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cadastros')
    dados = cursor.fetchall()
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

    # Verifica se os arquivos foram enviados corretamente
    comprovante = request.files.get('comprovante')
    documento = request.files.get('documento')

    if not nome or not comprovante or not documento:
        return "Erro: Todos os campos são obrigatórios!", 400  # Retorna erro se algum campo estiver vazio

    # Caminhos para salvar os arquivos
    comprovante_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(comprovante.filename))
    documento_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(documento.filename))

    # Salvar os arquivos
    comprovante.save(comprovante_path)
    documento.save(documento_path)

    # Salvar no banco de dados
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cadastros (nome, comprovante, documento) VALUES (?, ?, ?)",
                   (nome, comprovante.filename, documento.filename))
    conn.commit()
    conn.close()

    flash('Cadastro enviado com sucesso!')
    return redirect(request.referrer)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cadastros")
    cadastros = cursor.fetchall()
    conn.close()

    # Verificar se a pasta de imagens existe antes de listar os arquivos
    imagens_carrossel = []
    img_folder = os.path.join(os.getcwd(), 'static', 'img')

    if os.path.exists(img_folder):  # ✅ Verifica se a pasta existe
        imagens_carrossel = [
            f for f in os.listdir(img_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cadastros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/upload_carrossel', methods=['POST'])
def upload_carrossel():
    if 'imagem' not in request.files:
        return redirect(url_for('admin'))

    imagem = request.files['imagem']
    if imagem.filename == '':
        return redirect(url_for('admin'))

    if imagem:
        nome_arquivo = secure_filename(imagem.filename)
        caminho = os.path.join(app.static_folder, 'img', nome_arquivo)
        imagem.save(caminho)
    return redirect(url_for('admin'))


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
    nome_imagem = request.form['nome_imagem']
    caminho = os.path.join(app.static_folder, 'img', nome_imagem)
    if os.path.exists(caminho):
        os.remove(caminho)
    return redirect(url_for('admin'))




if __name__ == '__main__':
    app.run(debug=True)
