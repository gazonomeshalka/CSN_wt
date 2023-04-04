from flask import Flask, url_for, request, render_template, redirect

app = Flask(__name__)


@app.route('/company_page')
@app.route('/')
def company_page():
    params = {
        'company_page': True,
        'building_page': False,
        'specialization_page': False,
        'person_page': False
    }
    return render_template('base.html', **params)


def main():
    host, port = '127.0.0.1', 5000
    print(f'{host}:{port}')
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()