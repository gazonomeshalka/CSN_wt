from flask import Flask, url_for, request, render_template, redirect, session
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required
from data.users import User
from data.announces import Announce
from data.companies import Company
from data.stores import Store
from data.loginforms import LoginForm, RegisterForm, RegisterCompanyForm, RegisterStoreForm, ManageStoreDirectorForm
from data.passwords_func import create_key, check_password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tekmb1$)o@4)mg#-1fa@ubhxp%2v+bzlwn)yh53vyo68-x@a1&'
login_manager = LoginManager()
login_manager.init_app(app)


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
        login_user(user, remember=form.remember_me.data)
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
            login_user(user, remember=form.remember_me.data)
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
