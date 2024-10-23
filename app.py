from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secreta'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_prefixo TEXT UNIQUE,
            nome TEXT,
            ativo BOOLEAN
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS HorasExtras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            data DATE,
            horas FLOAT,
            FOREIGN KEY (funcionario_id) REFERENCES Funcionarios (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro_funcionario', methods=['POST'])
def cadastro_funcionario():
    cpf_prefixo = request.form['cpf_prefixo']
    nome = request.form['nome']
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Funcionarios (cpf_prefixo, nome, ativo) VALUES (?, ?, ?)',
                     (cpf_prefixo, nome, True))
        conn.commit()
        flash('Funcionário cadastrado com sucesso!')
    except sqlite3.IntegrityError:
        flash('Erro: CPF já cadastrado.')
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/editar_funcionario/<int:id>', methods=['POST'])
def editar_funcionario(id):
    nome = request.form['nome']
    ativo = request.form.get('ativo') == 'on'
    conn = get_db_connection()
    conn.execute('UPDATE Funcionarios SET nome = ?, ativo = ? WHERE id = ?', (nome, ativo, id))
    conn.commit()
    conn.close()
    flash('Funcionário atualizado com sucesso!')
    return redirect(url_for('index'))

@app.route('/desabilitar_funcionario/<int:id>', methods=['POST'])
def desabilitar_funcionario(id):
    conn = get_db_connection()
    conn.execute('UPDATE Funcionarios SET ativo = FALSE WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Funcionário desabilitado com sucesso!')
    return redirect(url_for('index'))

@app.route('/horas_extras', methods=['POST'])
def horas_extras():
    funcionario_id = request.form['funcionario_id']
    data = request.form['data']
    horas = request.form['horas']
    conn = get_db_connection()
    conn.execute('INSERT INTO HorasExtras (funcionario_id, data, horas) VALUES (?, ?, ?)',
                 (funcionario_id, data, horas))
    conn.commit()
    conn.close()
    flash('Horas extras cadastradas com sucesso!')
    return redirect(url_for('index'))

@app.route('/horas_extras_funcionario', methods=['POST'])
def horas_extras_funcionario():
    cpf_prefixo = request.form['cpf_prefixo']
    conn = get_db_connection()
    funcionario = conn.execute('SELECT * FROM Funcionarios WHERE cpf_prefixo = ?', (cpf_prefixo,)).fetchone()
    if funcionario:
        horas_extras = conn.execute('SELECT * FROM HorasExtras WHERE funcionario_id = ?', (funcionario['id'],)).fetchall()
        conn.close()
        return render_template('horas_extras.html', horas_extras=horas_extras, funcionario=funcionario)
    flash('Funcionário não encontrado.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
