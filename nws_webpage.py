from flask import Flask, render_template, redirect, url_for, request
import logging
from user import UserAccount, UserPage
from customer_page import WebPage

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('homepage'))


@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        if request.form['username'] and request.form['email'] and request.form['password']:
            user = UserAccount(request.form['username'], request.form['email'],request.form['password'])
            if user.authenticate():
                return redirect(url_for('user_session', username = request.form['username']))
            else:
                error = "Incorrect credentials, please check!"
        elif request.form['newusername'] and request.form['newemail'] and request.form['newpassword']:
            user = UserAccount(request.form['newusername'], request.form['newemail'], request.form['newpassword'])
            if user.create_account():
                return redirect(url_for('user_session', username = request.form['newusername']))
            else:
                error = "User is already registered, please sign in!"
    return render_template('homepage.html', error = error)


@app.route('/submission_successful', methods=['GET'])
def submission_successful():
    return render_template('submission_successful.html')


@app.route('/user_session/<username>', methods=['GET', 'POST'])
def user_session(username):
    return render_template('user_session.html', username = username)


@app.route('/create_webpage/<username>', methods=['GET', 'POST'])
def create_webpage(username):
    if request.method == 'POST':
        page = UserPage(request.form['url'], username, request.files['file'],
        redundancy = {'replicas' : request.form['replicas'],
        'server_selection': request.form['server_selection']})
        page.create()
    return render_template('create_webpage.html', username = username)


@app.route('/modify_webpage/<username>', methods=['GET', 'POST'])
def modify_webpage(username):
    return render_template('modify_webpage.html', username = username)


@app.route('/user_management/<username>', methods=['GET', 'POST'])
def user_management(username):
    """if request.method == 'POST':
        page = WebPage(request.form['url'], username)
        page.modify()"""
    return render_template('user_management.html', username = username)


@app.route('/upload_newindex/<username>', methods=['GET', 'POST'])
def upload_newindex(username):
    if request.method == 'POST':
        page = WebPage(request.form['url'], username, index_file = request.files['file'])
        page.modify(flag = 1)
    return render_template('upload_newindex.html', username = username)


@app.route('/revert_webpage/<username>', methods=['GET', 'POST'])
def revert_webpage(username):
    logging.info("Revert Request!!")
    reverted = False
    version_info = False
    if request.method == 'POST':
        page = WebPage(request.form['url'], username)
        files = page.get_index_files_list()
        for item in request.form.items():
            logging.info(item[0])
            if item[0] == "version_selection":
                version_info = True
                break
        if version_info:
            page.modify(flag = 2, requested_version = request.form['version_selection'])
            reverted = True
        return render_template('revert_webpage.html', username = username, files = files, reverted = reverted)
    return render_template('revert_webpage.html', username = username)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = '127.0.0.1', port = '9090', debug = True)
