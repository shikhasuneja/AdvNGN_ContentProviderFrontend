import os
import json
import logging
import ast
from werkzeug import secure_filename
from populatedb_api import populate_db
from shutil import copyfile

logging.basicConfig(level=logging.INFO)
NWS_CUSTOMERS_FILE = os.getcwd() + "/nws_customers.json"
NWS_CUSTOMER_PAGES_DIR = os.getcwd() + "/nws_urls"
populate_object = populate_db()

class UserAccount():

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def create_account(self):
        data = {}
        credentials = {self.email: {'username': self.username, 'email': self.email, 'password': self.password}}
        if not os.path.exists(NWS_CUSTOMERS_FILE):
            open(NWS_CUSTOMERS_FILE, 'a').close()
        else:
            with open(NWS_CUSTOMERS_FILE, 'r') as infile:
                data = infile.read()
        if data:
            if self.email in ast.literal_eval(data).keys():
                logging.info("User is already registered, please sign in!")
                return False
        logging.info("New Sign up, store credentials in the database!!")
        self._store_creds(data, credentials)
        logging.info("Sign-up successful!")
        return True

    def _store_creds(self, data, credentials):
        data = ast.literal_eval(data) if data else {}
        with open(NWS_CUSTOMERS_FILE, 'w') as outfile:
            data[list(credentials.keys())[0]] = list(credentials.values())[0]
            outfile.write(json.dumps(data))

    def authenticate(self):
        data = {}
        logging.info(self.email)
        creds = {self.email: {'username': self.username, 'email': self.email, 'password': self.password}}
        if not os.path.exists(NWS_CUSTOMERS_FILE):
            open(NWS_CUSTOMERS_FILE, 'a').close()
            return False
        else:
            with open(NWS_CUSTOMERS_FILE, 'r') as infile:
                data = infile.read()
        logging.info(ast.literal_eval(data).items())
        logging.info(ast.literal_eval(data).keys())
        user_data = ast.literal_eval(data)
        if user_data:
            if self.email in user_data.keys():
                logging.info(user_data[self.email])
                if user_data[self.email]['username'] == creds[self.email]['username'] and user_data[self.email]['email'] == creds[self.email]['email'] and user_data[self.email]['password'] == creds[self.email]['password']:
                    return True
        return False

    def find_details(self):
        with open(NWS_CUSTOMERS_FILE, 'r') as infile:
            data = infile.read()
        logging.info(list(ast.literal_eval(data).values()))
        users_list = list(ast.literal_eval(data).values())
        logging.info(self.username)
        for user in users_list:
            if user['username'] == self.username:
                return user

class UserPage():

    def __init__(self, url, user, index_file, redundancy):
        self.url = url
        self.user = user
        self.url_folder = NWS_CUSTOMER_PAGES_DIR + "/" + self.url
        self.users_file = self.url_folder + "/" + "users.json"
        self.curr_user_file = self.url_folder + "/" + "current_user.json"
        self.redundancy_reqs_file = self.url_folder + "/" + "redundancy.json"
        self.index_files_folder = self.url_folder + "/" + "files"
        self.website_version_file = self.index_files_folder + "/" + "webpage_version.json"
        self.redundancy_reqs = redundancy
        self.index_file = index_file

    def create(self):
        self._create_folders_and_files()
        self._save_user_details()
        self._save_redundancy_requirements()
        self._save_current_user_details()
        self._save_index_file()
        self._populate_db()

    def _create_folders_and_files(self):
        folders = [NWS_CUSTOMER_PAGES_DIR, self.url_folder, self.index_files_folder]
        files = [self.users_file, self.curr_user_file, self.redundancy_reqs_file, self.website_version_file]
        for folder in folders:
            if not os.path.exists(folder):
                os.mkdir(folder)
        for file in files:
            if not os.path.exists(file):
                open(file, 'a').close()

    def _save_user_details(self):
        user = UserAccount(self.user, None, None)
        user_details = user.find_details()
        admin_details = {self.user: {"email": user_details['email'],
        "password": user_details['password'], "role": "admin", "url":self.url}}
        with open(self.users_file, 'w') as outfile:
            outfile.write(json.dumps(admin_details))
        self._save_current_user_details()
        self._save_in_customer_db(admin_details)

    def _save_redundancy_requirements(self):
        selection_dict = {'aa': "Active_Active", "ab": "Active_Backup"}
        type_dict = {'same': 'same', 'diff': 'different'}
        reqs = {"url": self.url, "replicas": self.redundancy_reqs['replicas'],
        "selection": selection_dict[self.redundancy_reqs['server_selection'].split("_")[0]],
        "server_type": type_dict[self.redundancy_reqs['server_selection'].split("_")[1]]}
        with open(self.redundancy_reqs_file, 'w') as outfile:
            outfile.write(json.dumps(reqs))

    def _save_current_user_details(self):
        user = UserAccount(self.user, None, None)
        user_details = user.find_details()
        details = {"username": self.user, "email": user_details['email'], "password": user_details['password'], "role": "admin", "url":self.url}
        with open(self.curr_user_file, 'w') as outfile:
            outfile.write(json.dumps(details))

    def _save_index_file(self):
        self._save_intial_version_info()
        os.chdir(self.url_folder)
        self.index_file.save(secure_filename("index.html"))
        copyfile("index.html", self.index_files_folder + "/index_v1.html")

    def _save_intial_version_info(self):
        version_info = {"url": self.url, "requested_version": 1, "latest_version": 1}
        with open(self.website_version_file, 'w') as outfile:
            outfile.write(json.dumps(version_info))

    def _save_in_customer_db(self, admin):
        logging.info(admin)
        with open(NWS_CUSTOMERS_FILE, 'r') as infile:
            data = infile.read()
        logging.info(ast.literal_eval(data))
        data = ast.literal_eval(data)
        data[admin[self.user]['email']] = {"username": self.user, "email": admin[self.user]['email'],
        "password": admin[self.user]['password'], "url": self.url, "role": admin[self.user]['role'], "created": "True"}
        with open(NWS_CUSTOMERS_FILE, 'w') as outfile:
            outfile.write(json.dumps(data))

    def _populate_db(self):
        user = UserAccount(self.user, None, None)
        user_details = user.find_details()
        populate_object.api_account(user_details['email'])
        populate_object.api_account_users(user_details['email'], self.user)
        populate_object.api_cp_content(user_details['email'], "index_v1.html")
        populate_object.api_version(user_details['email'])
