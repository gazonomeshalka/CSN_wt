from flask import Flask, url_for, request, render_template, redirect
from data import db_session
from flask_login import LoginManager, login_user
from data.users import User
from data.loginforms import LoginForm

app = Flask(__name__)
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init("db/global.db")
    host, port = '127.0.0.1', 5000
    print(f'{host}:{port}')
    app.run(host=host, port=port)


if __name__ == '__main__':
    # ничего не добавлено, но под описания срока подходит
    main()