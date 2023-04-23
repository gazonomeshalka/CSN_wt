from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, SelectField,\
                    TextAreaField, FileField, DateTimeField
from wtforms.validators import DataRequired, Optional


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


class CreateAnnounceForm(FlaskForm):
    coverage = SelectField('Охват объявления', validators=[DataRequired()])
    title = StringField('Заголовок объявления', validators=(Optional(), ))
    description = TextAreaField('Описание объявления', validators=(Optional(), ))
    importance = SelectField('Важность объявления', validators=[DataRequired()],
                             choices=[(1, 'Важно'), (0, 'Не очень важно')])
    email = StringField('Почта, если объявление персонализированное', validators=(Optional(), ))
    specialization = SelectField('Специальность, если объявление специализированное', validators=(Optional(), ))
    del_time = StringField('Когда удалить объявление?', validators=[DataRequired()])
    submit = SubmitField('Создать')
