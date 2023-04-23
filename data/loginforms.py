from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    SNO = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterCompanyForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать')


class RegisterStoreForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать')


class ManageStoreDirectorForm(FlaskForm):
    boss_email = StringField('Почта босса', validators=[DataRequired()])
    address = SelectField('Адрес точки', validators=[DataRequired()])
    submit = SubmitField('Назначить')


class ManageStoreBossForm(FlaskForm):
    worker_email = StringField('Почта работника', validators=[DataRequired()])
    worker_specialization = StringField('Специальность работника', validators=[DataRequired()])
    submit = SubmitField('Назначить')
