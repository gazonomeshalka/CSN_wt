from flask import Flask, url_for, request, render_template, redirect, session
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required
from data.users import User
from data.announces import Announce
from data.companies import Company
from data.stores import Store
from data.loginforms import LoginForm, RegisterForm, RegisterCompanyForm, RegisterStoreForm, ManageStoreDirectorForm
from data.loginforms import ManageStoreBossForm, CreateAnnounceForm
from data.passwords_func import create_key, check_password
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import delete
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tekmb1$)o@4)mg#-1fa@ubhxp%2v+bzlwn)yh53vyo68-x@a1&'
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
login_manager = LoginManager()
login_manager.init_app(app)
scheduler = BackgroundScheduler()
scheduler.start()


@app.before_request
def make_session_permanent():
    session.permanent = True


def set_time_for_announce(id, time):
    global scheduler
    job = scheduler.add_job(func=del_announce, next_run_time=time, args=(id, ), id=str(id))
    print(id, time)
    return


def del_announce(id):
    db_sess = db_session.create_session()
    id = int(id)
    if db_sess.query(Announce).filter(Announce.id == id).first().file is not None:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        os.remove(os.path.join('static', app.config['UPLOAD_FOLDER'],
                               *[x for x in files if x[:x.rfind('.')] == str(id)]))
    conn = sqlite3.connect('db/global.db')
    c = conn.cursor()
    c.execute('''DELETE FROM announces WHERE id=?''', (id,))
    conn.commit()
    return


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/company_page', methods=['POST', 'GET'])
@app.route('/')
def company_page():
    params = {
        'company_page': True,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                announces = db_sess.query(Announce).filter(Announce.company_id == cur_user.company_id)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/building_page', methods=['POST', 'GET'])
def building_page():
    params = {
        'company_page': False,
        'building_page': True,
        'specialization_page': False,
        'person_page': False,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
                announces = db_sess.query(Announce).filter(Announce.store_id == cur_user.store_id,
                                                           Announce.specialization == None)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/specialization_page', methods=['POST', 'GET'])
def specialization_page():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': True,
        'person_page': False,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
                announces = db_sess.query(Announce).filter(Announce.store_id == cur_user.store_id,
                                                           Announce.specialization == cur_user.specialization)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/person_page', methods=['POST', 'GET'])
def person_page():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': True,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
                announces = db_sess.query(Announce).filter(Announce.receiver_id == cur_user.id)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Регистрация'
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title=title,
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title=title,
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            SNO=form.SNO.data,
            email=form.email.data,
            key_pass=create_key(form.password.data)
        )
        db_sess.add(user)
        db_sess.commit()
        logout_user()
        login_user(user, remember=True)
        session['user_id'] = user.id
        return redirect('/')
    return render_template('register.html', title=title, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Авторизация'
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and check_password(form.password.data, user.key_pass):
            logout_user()
            login_user(user, remember=True)
            session['user_id'] = user.id
            return redirect("/")
        return render_template('login.html',
                               title=title,
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title=title, form=form)


@app.route('/create_company', methods=['GET', 'POST'])
def create_company():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'Регистрация фирмы'
    }
    form = RegisterCompanyForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        company = Company()
        company.title = form.title.data
        company.CEO_id = session['user_id']
        if db_sess.query(Company).filter(Company.CEO_id == session['user_id']).first() is not None:
            return render_template('register_company.html', **params,
                                   form=form,
                                   message="На вас уже зарегистрирована фирма")
        elif db_sess.query(Company).filter(Company.title == company.title).first() is not None:
            return render_template('register_company.html', **params,
                                   form=form,
                                   message="Фирма с таким названием уже есть")
        elif db_sess.query(User).filter(User.id == session['user_id']).first().specialization is not None:
            return render_template('register_company.html', **params,
                                   form=form,
                                   message="Вы уже являетесь каким-то работником")
        director = db_sess.query(User).filter(User.id == session['user_id']).one()
        director.specialization = 'director'
        db_sess.add(company)
        db_sess.commit()
        director = db_sess.query(User).filter(User.id == session['user_id']).one()
        director.company_id = db_sess.query(Company).filter(Company.CEO_id == session['user_id']).one().id
        db_sess.commit()
        return redirect('/')
    return render_template('register_company.html', **params, form=form)


@app.route('/create_store', methods=['GET', 'POST'])
def create_store():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'Регистрация точки'
    }
    form = RegisterStoreForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        store = Store()
        store.address = form.address.data
        store.company_id = db_sess.query(Company).filter(Company.CEO_id == session['user_id']).first()
        if store.company_id is None:
            return render_template('register_store.html', **params,
                                   form=form,
                                   message="На вас ещё не зарегистрирована фирма")
        store.company_id = store.company_id.id
        if db_sess.query(Store).filter(Store.company_id == store.company_id, Store.address == store.address).first() \
                is not None:
            return render_template('register_store.html', **params,
                                   form=form,
                                   message="Можно зарегистрировать только одну точку на один адрес от фирмы")
        db_sess.add(store)
        db_sess.commit()
        return redirect('/')
    return render_template('register_store.html', **params, form=form)


@app.route('/manage_store_director', methods=['GET', 'POST'])
def manage_store_director():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'Управление точками'
    }
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == session['user_id']).first()
    stores = db_sess.query(Store).filter(Store.company_id == user.company_id).all()
    stores = [x.address for x in stores]
    stores = [(x, x) for x in stores]
    form = ManageStoreDirectorForm()
    form.address.choices = stores
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        address = form.address.data
        if db_sess.query(User).filter(User.email == form.boss_email.data).first() is None:
            return render_template('manage_store_director.html', **params,
                                   form=form,
                                   message="Пользователя с такой почтой ещё не существует")
        boss = db_sess.query(User).filter(User.email == form.boss_email.data).first()
        boss.specialization, boss.store_id, boss.company_id = ('boss',
                                                               db_sess.query(Store).filter(
                                                                   Store.address == address,
                                                                   Store.company_id == user.company_id).first().id,
                                                               user.company_id)
        store = db_sess.query(Store).filter(Store.address == address, Store.company_id == user.company_id).first()
        store.boss_id = boss.id
        db_sess.commit()
        return redirect('/')
    return render_template('manage_store_director.html', **params, form=form)


@app.route('/manage_store_boss', methods=['GET', 'POST'])
def manage_store_boss():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'Управление точками'
    }
    form = ManageStoreBossForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        w_e = form.worker_email.data
        w_s = form.worker_specialization.data
        if db_sess.query(User).filter(User.email == w_e).first() is None:
            return render_template('manage_store_boss.html', **params,
                                   form=form,
                                   message="Пользователя с такой почтой ещё не существует")
        worker = db_sess.query(User).filter(User.email == w_e).first()
        if worker.specialization is not None:
            return render_template('manage_store_boss.html', **params,
                                   form=form,
                                   message="Пользователь уже является чьим-то сотрудником.")
        boss = db_sess.query(User).filter(User.id == session['user_id']).first()
        worker.company_id, worker.store_id = boss.company_id, boss.store_id
        worker.specialization = w_s
        db_sess.commit()
        return redirect('/')
    return render_template('manage_store_boss.html', **params, form=form)


@app.route('/manage_store', methods=['GET', 'POST'])
def manage_store():
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.id == session['user_id']).first().specialization == 'director':
        return redirect('/manage_store_director')
    elif db_sess.query(User).filter(User.id == session['user_id']).first().specialization == 'boss':
        return redirect('/manage_store_boss')
    else:
        return redirect('/')


@app.route('/create_announce', methods=['GET', 'POST'])
def create_announce():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'Создание объявления'
    }
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == session['user_id']).first()
    form = CreateAnnounceForm()
    if user.specialization == 'director':
        choices = [('по фирме', 'по фирме')]
        form.specialization.choices = [('всем', 'всем')]
    elif user.specialization == 'boss':
        choices = [('по точке', 'по точке'), ('специализированные', 'специализированные'),
                   ('определённому лицу', 'определённому лицу')]
        form.specialization.choices = [(x.specialization, x.specialization) for x in
                                       db_sess.query(User).filter(User.company_id == user.company_id,
                                                                  User.store_id == user.store_id).all()]
    else:
        choices = [('специализированные', 'специализированные'), ('определённому лицу', 'определённому лицу')]
        form.specialization.choices = [(x.specialization, x.specialization) for x in
                                       db_sess.query(User).filter(User.company_id == user.company_id,
                                                                  User.store_id == user.store_id).all()]
    form.coverage.choices = choices
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        announce = Announce()
        announce.title = form.title.data
        announce.description = form.description.data
        announce.importance = form.importance.data
        announce.sender = user.SNO
        if form.coverage.data == 'по фирме':
            announce.company_id = user.company_id
        elif form.coverage.data == 'по точке':
            announce.store_id = user.store_id
        elif form.coverage.data == 'специализированные':
            announce.store_id = user.store_id
            announce.specialization = form.specialization.data
        elif form.coverage.data == 'определённому лицу':
            id = db_sess.query(User).filter(User.email == form.email.data).first().id
            announce.receiver_id = id
        try:
            time = datetime.datetime.strptime(form.del_time.data, '%Y-%m-%d %H:%M')
            now = datetime.datetime.now()
            if time <= now:
                return render_template('create_announce.html', **params,
                                       form=form,
                                       message="Время должно отличаться хотя-бы на минуту")
        except BaseException:
            return render_template('create_announce.html', **params,
                                   form=form,
                                   message="Неправильно введён формат времени")
        announce.del_time = str(time)
        db_sess.add(announce)
        db_sess.commit()
        if form.file.data.filename != '':
            file = form.file.data
            filename = secure_filename(file.filename)
            rasshirenie = filename.rfind('.')
            filename = str(announce.id) + filename[rasshirenie:]
            file_path = os.path.join('static', app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            announce.file = filename
        set_time_for_announce(announce.id, time)
        db_sess.commit()
        return redirect('/')
    return render_template('create_announce.html', **params, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/global.db")
    host, port = '127.0.0.1', 5000
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
