import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Configuração do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///capturas.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Captura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    especie = db.Column(db.String(100), nullable=False)
    numero_individuos = db.Column(db.Integer, nullable=False)
    local_captura = db.Column(db.String(100), nullable=False)
    numero_tombo = db.Column(db.String(50), nullable=False)
    quem_tombou = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)  # Nova coluna para informações detalhadas da espécie

# Criar banco de dados
with app.app_context():
    db.create_all()

# Página Inicial (Upload de Arquivo)
@app.route('/')
def index():
    return render_template("index.html")

# Rota para Upload do Excel
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        df = pd.read_excel(file)
        
        # Verifica se as colunas esperadas existem
        colunas_necessarias = {'Nome da Espécie', 'Número de Indivíduos', 'Local de Captura', 'Número do Tombo', 'Quem Tombou', 'Descrição'}
        if not colunas_necessarias.issubset(df.columns):
            return render_template("erro.html", mensagem="Erro: O arquivo Excel deve conter as colunas corretas!")

        # Adicionar os dados ao banco de dados
        for _, row in df.iterrows():
            captura = Captura(
                especie=row['Nome da Espécie'],
                numero_individuos=row['Número de Indivíduos'],
                local_captura=row['Local de Captura'],
                numero_tombo=row['Número do Tombo'],
                quem_tombou=row['Quem Tombou'],
                descricao=row['Descrição']
            )
            db.session.add(captura)

        db.session.commit()
        return redirect(url_for('listar_capturas'))
    return render_template("erro.html", mensagem="Erro ao enviar arquivo!")

# Página de Listagem das Capturas
@app.route('/capturas')
def listar_capturas():
    capturas = Captura.query.all()
    return render_template("capturas.html", capturas=capturas)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
