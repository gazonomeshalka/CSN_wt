from flask import Flask, url_for, request, render_template, redirect
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required
from data.users import User
from data.loginforms import LoginForm, RegisterForm
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
        'person_page': False
    }
    return render_template('base.html', **params)


@app.route('/building_page', methods=['POST', 'GET'])
def building_page():
    params = {
        'company_page': False,
        'building_page': True,
        'specialization_page': False,
        'person_page': False
    }
    return render_template('base.html', **params)


@app.route('/specialization_page', methods=['POST', 'GET'])
def specialization_page():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': True,
        'person_page': False
    }
    return render_template('base.html', **params)


@app.route('/person_page', methods=['POST', 'GET'])
def person_page():
    params = {
        'company_page': False,
        'building_page': False,
        'specialization_page': False,
        'person_page': True
    }
    return render_template('base.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Регистрация'
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
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
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title=title, form=form)


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