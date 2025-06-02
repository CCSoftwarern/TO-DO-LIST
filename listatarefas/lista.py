from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from listatarefas.auth import login_required
from listatarefas.db import get_db

bp = Blueprint('lista', __name__)

@bp.route('/')
@login_required
# <-- pega apenas as listas do usuário logado
def index():
    db = get_db()
    posts = db.execute(
        '''
        SELECT l.id, nome, Descricao, created, author_id, username
        FROM listadetarefas l
        INNER JOIN user u ON l.author_id = u.id
        WHERE l.author_id = ?
        ORDER BY created DESC
        ''',
        (g.user['id'],) 
    ).fetchall()
    return render_template('lista/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        error = None

        if not nome:
            error = 'Nome requerido.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO listadetarefas (nome, descricao, author_id)'
                ' VALUES (?, ?, ?)',
                (nome, descricao, g.user['id'])
            )
            db.commit()
            return redirect(url_for('lista.index'))

    return render_template('lista/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT l.id, nome, descricao, created, author_id, username'
        ' FROM listadetarefas l JOIN user u ON l.author_id = u.id'
        ' WHERE l.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        error = None

        if not nome:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE listadetarefas SET nome = ?, descricao = ?'
                ' WHERE id = ?',
                (nome, descricao, id)
            )
            db.commit()
            return redirect(url_for('lista.index'))

    return render_template('lista/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM listadetarefas WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('lista.index'))


@bp.route('/<int:id>/tarefas')
@login_required
def tarefas(id):
    db = get_db()
    
    # Verifica se a lista pertence ao usuário logado
    lista = db.execute(
        'SELECT id, nome FROM listaDeTarefas WHERE id = ? AND author_id = ?',
        (id, g.user['id'])
    ).fetchone()

    if lista is None:
        abort(404, "Lista não encontrada ou você não tem acesso.")

    # Busca as tarefas da lista
    tarefas = db.execute(
        '''
        SELECT t.id, t.Descricao AS descricao, t.created, t.ListaID AS lista_id
        FROM tarefas t
        WHERE t.ListaID = ?
        ORDER BY t.created DESC
        ''',
        (id,)
    ).fetchall()

    return render_template('tarefas/vertarefas.html', tarefas=tarefas, lista=lista)


#Criação da Tarefa

@bp.route('/<int:id>/createtarefa', methods=('GET', 'POST'))
@login_required
def createtarefa(id):
    if request.method == 'POST':
        descricao = request.form['descricao']
        status = request.form['status']
        ListaID = id
        error = None

        if not descricao:
            error = 'Nome requerido.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
            'INSERT INTO tarefas (descricao, status, ListaID) VALUES (?,?,?)',
            (descricao, status, ListaID)
                )

            db.commit()
            return redirect(url_for('lista.tarefas', id=id))

    return render_template('tarefas/createTarefa.html')

# Edição da Tarefa


@bp.route('/<int:id>/updatetarefa', methods=('GET', 'POST'))
@login_required
def updateTarefa(id):
    tarefa = get_post(id)

    if request.method == 'POST':
        descricao = request.form['descricao']
        status = request.form['status']
        error = None

        if not descricao:
            error = 'Descrição é requerido'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tarefas SET descricao = ?, status = ?'
                ' WHERE id = ?',
                (descricao, status, id)
            )
            db.commit()
            return redirect(url_for('lista.tarefas', id=id))

    return render_template('tarefas/updateTarefa.html', tarefa=tarefa)

# deletar tarefa
@bp.route('/<int:id>/deletetarefa', methods=('POST',))
@login_required
def deleteTarefa(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM tarefas WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('lista.tarefas', id=id))
