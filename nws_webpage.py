from flask import Flask, render_template, redirect, url_for, request
import logging
from user import UserAccount

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('homepage'))


@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    message = None
    if request.method == 'POST':
        if request.form['newusername'] and request.form['newemail'] and request.form['newpassword']:
            logging.info("New Sign up, store credentials in the database!!")
            admin = UserAccount(request.form['newusername'], request.form['newemail'], request.form['newpassword'])
            admin.create_account()
            return redirect(url_for('user_session'))
        #elif request.form['username'] != 'admin' or request.form['password'] != 'admin':
        #    error = 'Invalid Credentials. Please try again.'
        #else:
        #    return redirect(url_for('homepage'))
    return render_template('homepage.html', error = message)


@app.route('/submission_successful', methods=['GET'])
def submission_successful():
    return render_template('submission_successful.html')


@app.route('/user_session', methods=['GET'])
def user_session():
    return render_template('user_session.html')


@app.route('/create_webpage', methods=['GET'])
def create_webpage():
    return render_template('create_webpage.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', debug=True)
