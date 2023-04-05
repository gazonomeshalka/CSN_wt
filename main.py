from flask import Flask, url_for, request, render_template, redirect
from data import db_session

app = Flask(__name__)


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


def main():
    db_session.global_init("db/global.db")
    host, port = '127.0.0.1', 5000
    print(f'{host}:{port}')
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()