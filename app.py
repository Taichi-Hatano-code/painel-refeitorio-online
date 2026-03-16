from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from config import DATABASE_URL, SECRET_KEY 
from dbmanager import dbmanager
from datetime import datetime
import calendar

app = Flask(__name__)
app.secret_key = SECRET_KEY 

db = dbmanager(DATABASE_URL)

# --- Configuração do Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.get_colaborador_by_cpf(user_id)

# --- ROTAS ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))

    if request.method == 'POST':
        cpf = request.form.get('username')
        password = request.form.get('password')
        empresa_digitada = request.form.get('empresa')

        user = db.get_colaborador_by_cpf(cpf)
        
        if user and check_password_hash(user.senha, password):
            # 1. Verifica a empresa
            if user.empresa.lower().strip() == empresa_digitada.lower().strip():
                # 2. VERIFICAÇÃO DE ADMIN: O pulo do gato!
                if user.cargo.lower().strip() == 'admin':
                    login_user(user)
                    return redirect(url_for('feed'))
                else:
                    flash('⛔ Acesso Negado: Apenas administradores podem acessar este painel.')
            else:
                flash('❌ Empresa incorreta para este usuário.')
        else:
            flash('❌ CPF ou senha inválidos.')
            
    return render_template('login.html')

@app.route('/feed')
@login_required
def feed():
    # Segurança Dupla: Se alguém logado tentar acessar e não for admin, é expulso.
    if current_user.cargo.lower().strip() != 'admin':
        logout_user()
        flash('⛔ Sessão encerrada: Você não tem permissão de Admin.')
        return redirect(url_for('login'))

    data_filtro = request.args.get('data')
    filtro_mes = request.args.get('mes') # Formato: YYYY-MM
    tipo_filtro = request.args.get('tipo_refeicao') # <-- NOVO
    
    hoje = datetime.now()
    
    if filtro_mes:
        # Lógica para pegar o mês inteiro
        ano, mes = map(int, filtro_mes.split('-'))
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        inicio = datetime(ano, mes, 1)
        fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)
    elif data_filtro:
        # Lógica para um dia específico
        inicio = datetime.strptime(data_filtro, '%Y-%m-%d')
        fim = inicio.replace(hour=23, minute=59, second=59)
    else:
        # Padrão: Hoje
        inicio = hoje.replace(hour=0, minute=0, second=0)
        fim = hoje.replace(hour=23, minute=59, second=59)

    refeicoes = db.buscar_refeicoes_periodo(
        current_user.empresa, 
        inicio, 
        fim, 
        tipo=tipo_filtro
    )

    refeicoes = db.buscar_refeicoes_periodo(current_user.empresa, inicio, fim)
    
    return render_template('feed.html', refeicoes=refeicoes)

@app.route('/perfil/<cpf>')
@login_required
def perfil_funcionario(cpf):
    # Usa a função que você já tem (agora turbinada com joinedload)
    funcionario = db.get_colaborador_by_cpf(cpf)
    
    if not funcionario:
        flash("Funcionário não encontrado.")
        return redirect(url_for('feed'))
        
    # Ordena as refeições para aparecer a mais recente primeiro
    refeicoes_ordenadas = sorted(funcionario.refeicoes, key=lambda x: x.data, reverse=True)
    
    return render_template('perfil.html', funcionario=funcionario, refeicoes=refeicoes_ordenadas)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)