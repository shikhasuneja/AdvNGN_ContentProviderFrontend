import os
import json
import logging
import ast
from werkzeug import secure_filename
from shutil import copyfile
from populatedb_api import populate_db
from user import UserAccount, UserPage

logging.basicConfig(level=logging.INFO)
NWS_CUSTOMERS_FILE = os.getcwd() + "/nws_customers.json"
NWS_CUSTOMER_PAGES_DIR = os.getcwd() + "/nws_urls"
MODIFICATION_REASON = {0: "user_modification", 1: "new_upload", 2: "revert_request"}
populate_object = populate_db()

class WebPage():

    def __init__(self, url, user, index_file = None):
        self.url = url
        self.user = user
        self.url_folder = NWS_CUSTOMER_PAGES_DIR + "/" + self.url
        self.users_file = self.url_folder + "/" + "users.json"
        self.curr_user_file = self.url_folder + "/" + "current_user.json"
        self.redundancy_reqs_file = self.url_folder + "/" + "redundancy.json"
        self.index_files_folder = self.url_folder + "/" + "files"
        self.website_version_file = self.index_files_folder + "/" + "webpage_version.json"
        self.index_file = index_file

    def modify(self, flag, requested_version = None, user_details = {}):
        user_details = self._save_current_user_details()
        logging.info("Modifying the customer webpage")
        logging.info(MODIFICATION_REASON[flag])
        if MODIFICATION_REASON[flag] == "new_upload":
            logging.info("New \"index.html\" file is uploaded!")
            current_count = self._get_index_files_count()
            self._save_new_index_file(current_count + 1)
            self._populate_db_with_new_file(user_details, "index_v" + str(current_count + 1) + ".html")
        elif MODIFICATION_REASON[flag] == "user_modification":
            logging.info("User modification")
            logging.info(user_details)
            self._save_user_details(user_details)
        elif MODIFICATION_REASON[flag] == "revert_request":
            logging.info("Revert Request")
            logging.info(requested_version)
            self._revert_to_specific_version(requested_version)
            self._populate_db_with_version_info(user_details)

    def _save_version_info(self, version):
        version_info = {"url": self.url, "requested_version": version, "latest_version": version}
        with open(self.website_version_file, 'w') as outfile:
            outfile.write(json.dumps(version_info))

    def _save_new_index_file(self, version):
        self._save_version_info(version)
        os.chdir(self.url_folder)
        self.index_file.save(secure_filename("index.html"))
        copyfile(self.url_folder + "/index.html", self.index_files_folder + "/index_v" + str(version) + ".html")


    def _get_index_files_count(self):
        count = 0
        for root, dirs, files in os.walk(self.index_files_folder):
            for file in files:
                if "index" in file:
                    count += 1
        logging.info(count)
        return count

    def get_index_files_list(self):
        for root, dirs, files in os.walk(self.index_files_folder):
            index_files = [file for file in files if "index" in file]
        return index_files

    def _revert_to_specific_version(self, version):
        self._update_version_info(version)
        copyfile(self.index_files_folder + "/" + version, self.url_folder + "/index.html")

    def _update_version_info(self, version):
        with open(self.website_version_file, 'r') as infile:
            data = infile.read()
        logging.info(ast.literal_eval(data))
        version_info = ast.literal_eval(data)
        version_info["requested_version"] = version.split(".")[0].split("_v")[-1]
        with open(self.website_version_file, 'w') as outfile:
            outfile.write(json.dumps(version_info))

    def get_users(self):
        logging.info("Listing associated users!")
        with open(self.users_file, 'r') as infile:
            data = infile.read()
        logging.info(ast.literal_eval(data))
        users_dict = ast.literal_eval(data)
        return users_dict

    def _save_user_details(self, info):
        users = self.get_users()
        logging.info(users)
        users[info['username']] = {'email': info['email'], 'password': info['password'],
        'role': info['role'], 'url': self.url}
        with open(self.users_file, 'w') as outfile:
            outfile.write(json.dumps(users))
        self._save_user_info_in_customers_db(info)
        self._populate_db_with_user_info(info)

    def _save_user_info_in_customers_db(self, info):
        logging.info(info)
        with open(NWS_CUSTOMERS_FILE, 'r') as infile:
            data = infile.read()
        logging.info(ast.literal_eval(data))
        data = ast.literal_eval(data)
        data[info['email']] = {"username": info['username'], "email": info['email'], "password": info['password'], "url": self.url, "role": info['role'], "created": "False"}
        with open(NWS_CUSTOMERS_FILE, 'w') as outfile:
            outfile.write(json.dumps(data))

    def _save_current_user_details(self):
        user = UserAccount(self.user, None, None)
        user_details = user.find_details()
        details = {"username": self.user, "email": user_details['email'], "password": user_details['password'], "role": user_details['role'], "url":self.url}
        with open(self.curr_user_file, 'w') as outfile:
            outfile.write(json.dumps(details))
        return details

    def _populate_db_with_user_info(self, info):
        populate_object.api_account_users(info['email'], info['username'])

    def _populate_db_with_new_file(self, info, file):
        populate_object.api_cp_content(info['email'], file)

    def _populate_db_with_version_info(self, info):
        populate_object.api_version(info['email'])
