from flask import Flask, render_template, redirect, url_for, request
import logging, os
from user import UserAccount, UserPage
from customer_page import WebPage
from otp import OTP
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import tempfile, shutil

logging.basicConfig(level = logging.INFO)
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
    creation_successful = False
    if request.method == 'POST':
        page = UserPage(request.form['url'], username, request.files['file'],
        redundancy = {'replicas' : request.form['replicas'],
        'server_selection': request.form['server_selection']})
        page.create()
        creation_successful = True
    return render_template('create_webpage.html', username = username, creation_successful = creation_successful)


@app.route('/modify_webpage/<username>', methods=['GET', 'POST'])
def modify_webpage(username):
    return render_template('modify_webpage.html', username = username)


@app.route('/user_management/<username>', methods=['GET', 'POST'])
def user_management(username):
    logging.info("User Management Dashboard")
    return render_template('user_management.html', username = username)


@app.route('/upload_newindex/<username>', methods=['GET', 'POST'])
def upload_newindex(username):
    if request.method == 'POST':
        index_file = request.files['file']
        FileStorage(index_file).save("temp_index.html")
        page = WebPage(request.form['url'], username, index_file = index_file)
        error = page.modify(flag = 1)
        if error == "Permission Denied":
            return redirect(url_for('permission_denied'))
        if error == "OTP Authentication Required":
            return redirect(url_for('otp_authentication', url = request.form['url'], username = username, flag = 1))
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
            requested_version = request.form['version_selection']
            error = page.modify(flag = 2, requested_version = requested_version)
            if error == "Permission Denied":
                return redirect(url_for('permission_denied'))
            if error == "OTP Authentication Required":
                return redirect(url_for('otp_authentication', url = request.form['url'], username = username, flag = 2, requested_version = requested_version))
        return render_template('revert_webpage.html', username = username, files = files, reverted = reverted)
    return render_template('revert_webpage.html', username = username)


@app.route('/add_users/<username>', methods=['GET', 'POST'])
def add_users(username):
    submission_successful = False
    if request.method == 'POST':
        page = WebPage(request.form['url'], username)
        new_user_details = {'username': request.form['username'], 'email': request.form['email'],
        'password': request.form['password'], 'role': request.form['role']}
        error = page.modify(flag = 0, requested_version = None,
        new_user_details = new_user_details)
        if error == "Permission Denied":
            return redirect(url_for('permission_denied'))
        if error == "OTP Authentication Required":
            return redirect(url_for('otp_authentication', url = request.form['url'], username = username, flag = 0, new_user_details = new_user_details))
        submission_successful = True
    return render_template('add_users.html', username = username, submission_successful = submission_successful)


@app.route('/list_existing_users/<username>', methods=['GET', 'POST'])
def list_existing_users(username):
    if request.method == 'POST':
        for item in request.form.items():
            logging.info(item[0])
            if item[0] == "url":
                page = WebPage(request.form['url'], username)
                users = page.get_users()
                return render_template('list_existing_users.html', username = username, users = users)
    return render_template('list_existing_users.html', username = username)


@app.route('/remove_users/<username>', methods=['GET', 'POST'])
def remove_users(username):
    return render_template('remove_users.html', username = username)


@app.route('/permission_denied', methods=['GET', 'POST'])
def permission_denied():
    return render_template('permission_denied.html')


@app.route('/otp_authentication', methods=['GET', 'POST'])
def otp_authentication():
    url = request.args.get('url')
    username = request.args.get('username')
    flag = request.args.get('flag')
    otp = OTP(url)
    if request.method == 'GET':
        otp.send_email(username)
    elif request.method == 'POST':
        status = otp.match_otp(request.form['otp'])
        if not status:
            return render_template('otp_authentication.html', status = status)
        else:
            if flag == "0":
                page = WebPage(url, username)
                page.modify(flag = 0, requested_version = None,
                new_user_details = request.args.get('new_user_details'), otp_authentication = True)
                submission_successful = True
                return render_template('add_users.html', username = username, submission_successful = submission_successful)
            elif flag == "1":
                page = WebPage(url, username)
                page.modify(flag = 1, otp_authentication = True)
                submission_successful = True
                return render_template('upload_newindex.html', username = username, submission_successful = submission_successful)
            elif flag == "2":
                page = WebPage(url, username)
                page.modify(flag = 2, requested_version = request.args.get('requested_version'), otp_authentication = True)
                reverted = True
                return render_template('revert_webpage.html', username = username, reverted = reverted)
    return render_template('otp_authentication.html', status = True)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = '0.0.0.0', port = 9090, debug = True)
