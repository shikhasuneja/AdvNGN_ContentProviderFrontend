from flask import Flask, render_template, redirect, url_for, request
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('homepage'))


@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        print("Post Request")
        if request.form['newusername'] and request.form['newpassword']:
            print("New Sign up, store credentials in the database!!")
        elif request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('homepage'))
    return render_template('homepage.html', error=error)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', debug=True)
