import os
import json
import logging
import ast

logging.basicConfig(level=logging.INFO)
NWS_CUSTOMERS_FILE = "nws_customers.json"
NWS_CUSTOMER_PAGES_DIR = "nws_urls"

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
        credentials = {self.email: {'username': self.username, 'email': self.email, 'password': self.password}}
        with open(NWS_CUSTOMERS_FILE, 'r') as infile:
            data = infile.read()
        logging.info(list(ast.literal_eval(data).items()))
        if data:
            if self.email in ast.literal_eval(data).keys():
                if ast.literal_eval(data)[self.email] == credentials[self.email]:
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

    def __init__(self, url, admin_user, redundancy):
        self.url = url
        self.admin = admin_user
        self.url_folder = NWS_CUSTOMER_PAGES_DIR + "/" + self.url
        self.users_file = self.url_folder + "/" + "users.json"
        self.curr_user_file = self.url_folder + "/" + "current_user.json"
        self.redundancy_reqs_file = self.url_folder + "/" + "redundancy.json"
        self.index_files_folder = self.url_folder + "/" + "files"
        self.website_version_file = self.index_files_folder + "/" + "webpage_version.json"
        self.redundancy_reqs = redundancy

    def create(self):
        self._create_folders_and_files()
        self._save_admin_details()
        self._save_redundancy_requirements()
        self._save_current_user_details()

    def _create_folders_and_files(self):
        folders = [NWS_CUSTOMER_PAGES_DIR, self.url_folder, self.index_files_folder]
        files = [self.users_file, self.curr_user_file, self.redundancy_reqs_file, self.website_version_file]
        for folder in folders:
            if not os.path.exists(folder):
                os.mkdir(folder)
        for file in files:
            if not os.path.exists(file):
                open(file, 'a').close()

    def _save_admin_details(self):
        user = UserAccount(self.admin, None, None)
        user_details = user.find_details()
        admin_details = {"username": self.admin, "email": user_details['email'], "password": user_details['password'], "role": "admin", "url":self.url}
        with open(self.users_file, 'w') as outfile:
            outfile.write(json.dumps(admin_details))

    def _save_redundancy_requirements(self):
        selection_dict = {'aa': "Active_Active", "ab": "Active_Backup"}
        type_dict = {'same': 'same', 'diff': 'different'}
        reqs = {"url": self.url, "replicas": self.redundancy_reqs['replicas'],
        "selection": selection_dict[self.redundancy_reqs['server_selection'].split("_")[0]],
        "server_type": type_dict[self.redundancy_reqs['server_selection'].split("_")[1]]}
        with open(self.redundancy_reqs_file, 'w') as outfile:
            outfile.write(json.dumps(reqs))

    def _save_current_user_details(self):
        user = UserAccount(self.admin, None, None)
        user_details = user.find_details()
