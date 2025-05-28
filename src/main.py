from flask import Flask, render_template, redirect, url_for, flash
from src.models import db
from src.routes import main_bp, employee_bp, time_record_bp, holiday_bp, calculation_bp, import_xlsx_bp
from src.routes.manual_entry import manual_entry_bp
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sistema_ponto_secretkey')

# Configuração do banco de dados para ambiente de produção
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
    f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db.init_app(app)

# Registrar blueprints
app.register_blueprint(main_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(time_record_bp)
app.register_blueprint(holiday_bp)
app.register_blueprint(calculation_bp)
app.register_blueprint(import_xlsx_bp)  # Blueprint para importação de planilhas
app.register_blueprint(manual_entry_bp)  # Novo blueprint para entrada manual de registros

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Em produção, o servidor WSGI fornecerá a porta
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
