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
    return render_template('index.html')

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

@app.route('/upload-imagem-carrossel', methods=['POST'])
def upload_imagem_carrossel():
    imagem = request.files.get('imagem')
    if imagem:
        nome_arquivo = secure_filename(imagem.filename)
        caminho = os.path.join('static', 'img', nome_arquivo)
        imagem.save(caminho)
        flash('Imagem adicionada ao carrossel com sucesso!')
    else:
        flash('Erro ao enviar imagem.')
    return redirect(request.referrer)





if __name__ == '__main__':
    app.run(debug=True)
