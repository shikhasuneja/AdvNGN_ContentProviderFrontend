import json
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

class populate_db():
    def __init__(self,db_Server_ip="192.168.100.1", db_Server_port='31002'):
        self.db_Server_ip=db_Server_ip
        self.db_Server_port=db_Server_port
        self._users='users.json'
        self.redundancy='redundancy.json'
        self.current_user='current_user.json'
        self._files='files'
        self.webpage_version="webpage_version.json"
        self.nws_customers= CURR_DIR + "/nws_customers.json"
        self.headers= {'Content-type': 'application/json'}


    def api_account(self,admin_user_email):
                        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
                        with open('{}/nws_urls/{}/{}'.format(CURR_DIR, url,self.redundancy)) as a1:
                            redundancyD = json.load(a1)
                            dictforaccountcreation={'url':'{}'.format(url),'selection':'{}'.format(redundancyD['selection']), 'current_version': '1', 'type_server': '{}'.format(redundancyD['server_type']), 'replica': '{}'.format(redundancyD['replicas'])}
                            body='account'
                            logging.info(body)
                            logging.info(dictforaccountcreation)
                            self.post_cred(body,dictforaccountcreation) #1


    def api_cp_content(self,admin_user_email,i1):
        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
        index_file_check=os.listdir('{}/nws_urls/{}/{}'.format(CURR_DIR, url,"files"))
        with open('{}/nws_urls/{}/{}/{}'.format(CURR_DIR, url,"files",i1),'r') as a2:
                                index_content=a2.read()
                                body="cp/content"
                                dictforaccountcreation={"username":"{}".format(admin_user),"password":"{}".format(admin_user_pwd),"version":"{}".format(i1[7]),"url":"{}".format(url),"data":"{}".format(index_content)}
                                logging.info(body)
                                logging.info(dictforaccountcreation)
                                self.post_cred(body,dictforaccountcreation) #3

    def api_account_users(self,admin_user_email,user_name_explicit):
            url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
            j=user_name_explicit
            with open('{}/nws_urls/{}/{}'.format(CURR_DIR, url,self._users)) as a2:
                        userD = json.load(a2)
                        if userD[j]['role']=='admin':
                             owner=True
                        else:
                             owner=False
                        dictforaccountcreation= {"username":"{}".format(j),"password":"{}".format(userD[j]['password']),"url":"{}".format(userD[j]['url']),"email":"{}".format(userD[j]['email']),"owner":owner}
                        body='account/users'
                        logging.info(body)
                        logging.info(dictforaccountcreation)
                        self.post_cred(body,dictforaccountcreation) #no 4

    def api_version(self,admin_user_email):
        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
        with open('{}/nws_urls/{}/{}/{}'.format(CURR_DIR, url,"files","webpage_version.json")) as a2:
                                versionD=json.load(a2)
                                body="account/version"
                                dictforaccountcreation={"url":"{}".format(url),"username":"admin","password":"admin","current_version":"{}".format(versionD['requested_version'])}
                                logging.info(body)
                                logging.info(dictforaccountcreation)
                                self.post_cred(body,dictforaccountcreation) #4


    def tryimport(self,admin_user_email):
                with open(self.nws_customers) as m:
                                allcustomerD = json.load(m)
                                i=admin_user_email
                                url=allcustomerD[i]['url']
                                admin_user_pwd=allcustomerD[i]['password']
                                admin_user=allcustomerD[i]['username']
                                admin_user_role='True'
                                return (url,admin_user,admin_user_pwd)

    def post_cred(self,body,expected_dict):
                r = requests.post('http://{}:{}/{}'.format(self.db_Server_ip, self.db_Server_port,body), data=(json.dumps(expected_dict)), headers=self.headers)
                logging.info(r.status_code)
