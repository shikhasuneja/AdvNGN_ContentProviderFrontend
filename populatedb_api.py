import http.client
import json
import requests
import os

class populate_db():
    def __init__(self,db_Server_ip="10.201.2.150", db_Server_port='9191'):
        self.db_Server_ip=db_Server_ip
        self.db_Server_port=db_Server_port
        self._users='users.json'
        self.redundancy='redundancy.json'
        self.current_user='current_user.json'
        self._files='files'
        self.webpage_version="webpage_version.json"
        self.nws_customers="nws_customers.json"
        self.headers= {'Content-type': 'application/json', 'Accept': 'text/plain'}


    def api_account(self,admin_user_email):
                        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
                        with open('nws_urls/{}/{}'.format(url,self.redundancy)) as a1:
                            redundancyD = json.load(a1)
                            dictforaccountcreation={'url':'{}'.format(url),'selection':'{}'.format(redundancyD['selection'])}
                            body='/account'
                            print(body,"--",dictforaccountcreation)
                            #self.post_cred(body,dictforaccountcreation) #1


    def api_cp_content(self,admin_user_email,i1):
        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
        index_file_check=os.listdir('nws_urls/{}/{}'.format(url,"files"))
        with open('nws_urls/{}/{}/{}'.format(url,"files",i1),'r') as a2:
                                index_content=a2.read()
                                body="/cp/content"
                                dictforaccountcreation={"username":"{}".format(admin_user),"password":"{}".format(admin_user_pwd),"version":"{}".format(i1[7]),"url":"{}".format(url),"data":"{}".format(index_content)}
                                print(body,"--",dictforaccountcreation)
                                #self.post_cred(body,dictforaccountcreation) #3

    def api_account_users(self,admin_user_email,user_name_explicit):
            url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
            j=user_name_explicit
            with open('nws_urls/{}/{}'.format(url,self._users)) as a2:
                        userD = json.load(a2)
                        if userD[j]['role']=='admin':
                             owner=True
                        else:
                             owner=False
                        dictforaccountcreation= {"username":"{}".format(j),"password":"{}".format(userD[j]['password']),"url":"{}".format(userD[j]['url']),"email":"{}".format(userD[j]['email']),"owner":"{}".format(owner)}
                        body='/account/users'
                        print(body,"--",dictforaccountcreation)
                        #self.post_cred(body,dictforaccountcreation) #no 4

    def api_version(self,admin_user_email):
        url,admin_user,admin_user_pwd=self.tryimport(admin_user_email)
        with open('nws_urls/{}/{}/{}'.format(url,"files","webpage_version.json")) as a2:
                                versionD=json.load(a2)
                                body="/account/version"
                                dictforaccountcreation={"url":"{}".format(url),"username":"admin","password":"admin","current_version":"{}".format(versionD['requested_version'])}
                                print(body,"--",dictforaccountcreation)
                                #self.post_cred(body,dictforaccountcreation) #4


    def tryimport(self,admin_user_email):
                with open(self.nws_customers) as m:
                                allcustomerD = json.load(m)
                                i=admin_user_email
                                url=allcustomerD[i]['url']
                                self.cust_dict.append(url)
                                admin_user_pwd=allcustomerD[i]['password']
                                admin_user=allcustomerD[i]['username']
                                admin_user_role='True'
                                return (url,admin_user,admin_user_pwd)

    def post_cred(self,body,expected_dict):
                r = requests.post('http://{}:{}/{}'.format(self.db_Server_ip, self.db_Server_port,body), data=(expected_dict), headers=self.headers)
                print(r.status_code)
