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
import sqlite3
import os
from werkzeug.utils import secure_filename

# подготовка к работе
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tekmb1$)o@4)mg#-1fa@ubhxp%2v+bzlwn)yh53vyo68-x@a1&'
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
login_manager = LoginManager()
login_manager.init_app(app)
scheduler = BackgroundScheduler()
scheduler.start()


@app.before_request
def make_session_permanent():
    """Функция устанавливает то, что сессия будет перманентна."""
    session.permanent = True


def set_time_for_announce(id, time):
    """Функция добавляет работу для модуля schedule, в следствии чего, объявление позже будет удалено"""
    global scheduler
    job = scheduler.add_job(func=del_announce, next_run_time=time, args=(id, ), id=str(id))
    print(id, time)
    return


def del_announce(id):
    """Функция удаляет объявление"""
    db_sess = db_session.create_session()
    id = int(id)
    # удаление прикрепленного к объявлению файла, если он был
    if db_sess.query(Announce).filter(Announce.id == id).first().file is not None:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        os.remove(os.path.join('static', app.config['UPLOAD_FOLDER'],
                               *[x for x in files if x[:x.rfind('.')] == str(id)]))
    conn = sqlite3.connect('db/global.db')
    c = conn.cursor()
    c.execute('''DELETE FROM announces WHERE id=?''', (id,))
    # подтверждение действия
    conn.commit()
    return


@login_manager.user_loader
def load_user(user_id):
    """Функция возвращает пользователя по его"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)
    # А я совсем забыл про неё, когда работал над проектом ;(


@app.route('/company_page', methods=['POST', 'GET'])
@app.route('/')
def company_page():
    """Страница с объявлениями, отсортированными по фирме"""
    params = {
        'company_page': True,
        'building_page': False,
        'specialization_page': False,
        'person_page': False,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    # работает, если пользователь зарегистрирован и авторизован
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                # сортировка объявлений по фирме
                announces = db_sess.query(Announce).filter(Announce.company_id == cur_user.company_id)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/building_page', methods=['POST', 'GET'])
def building_page():
    """Страница с объявлениями, отсортированными по предприятию"""
    params = {
        'company_page': False,
        'building_page': True,
        'specialization_page': False,
        'person_page': False,
        'title': 'CSN'
    }
    db_sess = db_session.create_session()
    # работает, если пользователь зарегистрирован и авторизован
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                # сортировка объявлений по предприятию
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
    # работает, если пользователь зарегистрирован и авторизован
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                # сортировка объявлений по специализации пользователя и фирме
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
    # работает, если пользователь зарегистрирован и авторизован
    if session.get('user_id', False):
        cur_user = db_sess.query(User).filter(User.id == session['user_id']).first()
        if cur_user is not None:
            if cur_user.specialization:
                # сортировка объявлений по айди пользователя
                announces = db_sess.query(Announce).filter(Announce.receiver_id == cur_user.id)
                params['announces'] = announces
    return render_template('base.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Функция для регистрации пользователя"""
    title = 'Регистрация'
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:  # если пароли не совпадают, то это пишется
            return render_template('register.html', title=title,
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        # если почта уже зарегистрирована, то об этом сообщается
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title=title,
                                   form=form,
                                   message="Такой пользователь уже есть")
        # создание аккаунта пользователя
        user = User(
            SNO=form.SNO.data,
            email=form.email.data,
            key_pass=create_key(form.password.data)
        )
        db_sess.add(user)
        db_sess.commit()
        # авторизация в системе
        logout_user()
        login_user(user, remember=True)
        session['user_id'] = user.id
        return redirect('/')
    return render_template('register.html', title=title, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция показывает окно для авторизации и авторизует пользователя"""
    title = 'Авторизация'
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # проверка пароля
        if user and check_password(form.password.data, user.key_pass):
            # авторизация пользователя
            logout_user()
            login_user(user, remember=True)
            session['user_id'] = user.id
            return redirect("/")
        # если пароль не подходит, страница грузится заново
        return render_template('login.html',
                               title=title,
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title=title, form=form)


@app.route('/create_company', methods=['GET', 'POST'])
def create_company():
    """Функция создаёт фирму и показывает соответствующий интерфейс"""
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
        # создание фирмы
        company = Company()
        company.title = form.title.data
        company.CEO_id = session['user_id']
        # проверка запроса на возможность выполнения
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
        # если все подходит, то создается фирма и коммитятся изменения
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
    """Функция создает предприятие (точку) и отображает соответствующий интерфейс"""
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
        # создание точки
        store = Store()
        store.address = form.address.data
        store.company_id = db_sess.query(Company).filter(Company.CEO_id == session['user_id']).first()
        # проверка на валидность запроса
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
    """Функция дает возможность работы с точками для директора"""
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
    form.address.choices = stores  # программа дает выбор из уже созданных точек
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        address = form.address.data
        # проверка почты
        if db_sess.query(User).filter(User.email == form.boss_email.data).first() is None:
            return render_template('manage_store_director.html', **params,
                                   form=form,
                                   message="Пользователя с такой почтой ещё не существует")
        # назначение начальника
        boss = db_sess.query(User).filter(User.email == form.boss_email.data).first()
        boss.specialization, boss.store_id, boss.company_id = ('boss',
                                                               db_sess.query(Store).filter(
                                                                   Store.address == address,
                                                                   Store.company_id == user.company_id).first().id,
                                                               user.company_id)
        # изменение айди босса у магазина
        store = db_sess.query(Store).filter(Store.address == address, Store.company_id == user.company_id).first()
        store.boss_id = boss.id
        db_sess.commit()
        return redirect('/')
    return render_template('manage_store_director.html', **params, form=form)


@app.route('/manage_store_boss', methods=['GET', 'POST'])
def manage_store_boss():
    """Функция дает возможность работы с точками для начальника"""
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
        # собираем данные о новом работнике
        w_e = form.worker_email.data
        w_s = form.worker_specialization.data
        # проверка запроса на валидность
        if db_sess.query(User).filter(User.email == w_e).first() is None:
            return render_template('manage_store_boss.html', **params,
                                   form=form,
                                   message="Пользователя с такой почтой ещё не существует")
        worker = db_sess.query(User).filter(User.email == w_e).first()
        if worker.specialization is not None:
            return render_template('manage_store_boss.html', **params,
                                   form=form,
                                   message="Пользователь уже является чьим-то сотрудником.")
        # привязка работника
        boss = db_sess.query(User).filter(User.id == session['user_id']).first()
        worker.company_id, worker.store_id = boss.company_id, boss.store_id
        worker.specialization = w_s
        db_sess.commit()
        return redirect('/')
    return render_template('manage_store_boss.html', **params, form=form)


@app.route('/manage_store', methods=['GET', 'POST'])
def manage_store():
    """Функция перенаправляет на нужную страницу, учитывая вашу должность"""
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.id == session['user_id']).first().specialization == 'director':
        return redirect('/manage_store_director')
    elif db_sess.query(User).filter(User.id == session['user_id']).first().specialization == 'boss':
        return redirect('/manage_store_boss')
    else:  # если вы не являетесь боссом или директором, редактирование точек для вас закрыто
        return redirect('/')


@app.route('/create_announce', methods=['GET', 'POST'])
def create_announce():
    """Функция создает объявления и показывает соответствующий интерфейс"""
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
    # подбор опций по охвату объявление в зависимости от специализации (должности)
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
        # создание объявления, сбор данных
        announce = Announce()
        announce.title = form.title.data
        announce.description = form.description.data
        announce.importance = form.importance.data
        announce.sender = user.SNO
        # характеристики объявления в базе данных зависят от его охвата
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
        try:  # получение времени удаления объявления
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
        db_sess.commit()  # запись
        # запись прикрепленного файла, если он есть
        if form.file.data.filename != '':
            file = form.file.data
            filename = secure_filename(file.filename)
            rasshirenie = filename.rfind('.')
            filename = str(announce.id) + filename[rasshirenie:]
            file_path = os.path.join('static', app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            announce.file = filename
        set_time_for_announce(announce.id, time)  # установка времени удаления объявления
        db_sess.commit()
        return redirect('/')
    return render_template('create_announce.html', **params, form=form)


@app.route('/logout')
@login_required
def logout():
    """Функция разлогинивает пользователя"""
    logout_user()
    return redirect("/")


def main():
    """Основания функция"""
    db_session.global_init("db/global.db")
    host, port = '127.0.0.1', 5000
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
