#Advanced NGN: Rotational Program
#File: Database Server - Content Provider Front End
#Writer: Rohit Dilip Kulkarni
#Team Members: Mansi, Shikha, Rohit
#Dated: 31 March 2019

from flask import Flask, jsonify, request, render_template, Response
import json
import os
import requests
import time
import threading

app = Flask(__name__)
"""
/api/version
    GET: Gets the version number
        JSON: NONE
        RETURN TRUE: {"success":True,"cp_version":1}

/cp/content
    GET: Gets the contents of the customers files
        JSON:           {"username":"angn","password":"abcd","version":"12","url":"angn.com"}
        RETURN TRUE:    {'success':True,'data':file_data}
        RETURN FALSE:   {'success':False,'comment':'Unauthorized Access'}
                        {'success':False,'comment':'No such version found'}
                        CHECKS:
                        {'success':False,'comment':'Need admin username'}
                        {'success':False,'comment':'Need admin password'}
                        {'success':False,'comment':'Need version number'}

    POST: Push the customers data
        JSON: {"username":"angn","password":"abcd","version":"12","url":"angn.com","data":"http file data"}
        RETURN TRUE:    {'success':True}
        RETURN FALSE:   CHECKS

/account
    GET: All the information of acccount db - only for admin
        JSON:           {"username":"admin","password":"admin"}
        RETURN TRUE:    {'success':True,'data':file_data - of cp_account_detail}
        RETURN FALSE:   {'success':False,'comment':'Unauthorized Access'}
                        CHECKS

    POST: Creates new accounts
        JSON:           {"url":"angn.com","selection":"active-active","type_server":"different","replica":2}
        RETURN TRUE:    {'success':True}
        RETURN FALSE:   CHECKS

/account/users
    GET: All the information of users db - only for admin
        JSON:           {"username":"admin","password":"admin"}
        RETURN TRUE:    {'success':True,'data':file-data of user_db}
        RETURN FALSE:   {'success':False,'comment':'Unauthorized Access'}
                        CHECKS

    POST: Creates new accounts
        JSON:           {"username":"angn","password":"abcd","url":"mainpage.com","email":"boo@angn.com","owner":True}
        RETURN TRUE:    {'success':True}
        RETURN FALSE:   CHECKS


/cp/network
    GET: for cp network data
        JSON:           {"username":"admin","password":"admin"}
        RETURN TRUE:    {'success':True,'data':customer_db - info for cp backend}
        RETURN FALSE:   CHECKS

/cp/statistics
    GET: All the information of statistics db - only for admin
        JSON:           {"username":"admin","password":"admin"}
        RETURN TRUE:    {'success':True,'data':file-data of statistics}
        RETURN FALSE:   {'success':False,'comment':'Unauthorized Access'}
                        CHECKS

    POST: Creates new file for statistics
        JSON:           {"username":"admin","password":"admin","statistics":{},"other":{}}
        RETURN TRUE:    {'success':True}
        RETURN FALSE:   CHECKS

/synch
    GET: Information for server synch

/synch/files
    GET: Sych the files from promary server
"""

@app.route('/api/version', methods=['GET'])
def get_tasks():
    global cp_version
    return Response(json.dumps({'success':True,'cp_version':cp_version}), status=200, mimetype='application/json')

@app.route('/cp/content',methods=['GET','POST'])
#for main file service
def creating_file():
    global cp_version
    if request.method == "POST":
        data=request.json
        checks,filename,edit_check=creating_file_checks(data)
        if checks != True:
            return checks
        else:
            if edit_check != True:
                return (edit_check)

            with open(filename,'w') as fl:
                json.dump(data, fl)
            cp_version+=1
            return (Response(json.dumps({'success':True}), status=200, mimetype='application/json'))

    elif request.method == "GET":
        data=request.json
        checks,filename,edit_check=creating_file_checks(data)
        if checks != True:
            return checks
        else:
            if os.path.isfile(filename):
                with open(filename, 'r') as fl:
                    file_data = json.load(fl)
                return (Response(json.dumps({'success':True,'data':file_data}), status=200, mimetype='application/json'))
            else:
                return (Response(json.dumps({'success':False,'comment':'File not found - Incorect Version'}), status=400, mimetype='application/json'))

def creating_file_checks(data):
    global user_db
    #return the HTTP - json error and filename
    if 'username' not in data.keys(): #check if username field present in json
        return ((Response(json.dumps({'success':False,'comment':'Need admin username'}), status=400, mimetype='application/json')),False,False)
    elif 'password' not in data.keys(): #check if password field present in json
        return ((Response(json.dumps({'success':False,'comment':'Need admin password'}), status=400, mimetype='application/json')),False,False)
    elif 'version' not in data.keys(): #check if version field present in json
        return ((Response(json.dumps({'success':False,'comment':'Need version number'}), status=400, mimetype='application/json')),False,False)
    elif 'url' not in data.keys(): #check if version field present in json
        return ((Response(json.dumps({'success':False,'comment':'Need url for webpage'}), status=400, mimetype='application/json')),False,False)
    else:
        if data['username'] != 'admin' and data['password'] != user_db['admin']['password']: #global access to admin
            if data['username'] not in user_db.keys():
                return ((Response(json.dumps({'success':False,'comment':'No user found'}), status=400, mimetype='application/json')),False,False)
            elif data['password'] != user_db[data['username']]["password"]:
                return ((Response(json.dumps({'success':False,'comment':'Incorrect Password'}), status=400, mimetype='application/json')),False,False)
            elif data['url'] != user_db[data['username']]["url"]:
                return ((Response(json.dumps({'success':False,'comment':'Incorrect url edit request'}), status=400, mimetype='application/json')),False,False)

        if user_db[data['username']]['owner'] != True: #check if the user is able to edit
            edit_check=(Response(json.dumps({'success':False,'comment':'User has no auth to edit'}), status=400, mimetype='application/json'))
        else:
            edit_check=True

        filename="cp_"+data['url']+"_"+data["version"]+".json"
        return (True,filename,edit_check)


def admin_request_file(data):
    #data {"username":"admin","password":"admin","filename":"<file>"}
    global user_db
    if sorted(['username','password','filename']) == sorted(data.keys()):
        if data['username']=='admin' and data['password'] == user_db['admin']['password']:
            if not os.path.isfile(data['filename']):
                return (Response(json.dumps({'success':False,'comment':'File not present in server'}), status=400, mimetype='application/json'))

            with open(data['filename'], 'r') as fl:
                data = json.load(fl)
            return (Response(json.dumps({'success':True,'data':data}), status=200, mimetype='application/json'))
        else:
            return (Response(json.dumps({'success':False,'comment':'Unauthorized Access'}), status=400, mimetype='application/json'))

    else:
        return (Response(json.dumps({'success':False,'comment':'Need admin username and password'}), status=400, mimetype='application/json'))

@app.route('/account',methods=['GET','POST'])
#for account details username and password
def acount_details():
    global cp_version
    global primary_master
    global secondary_master
    global account_db
    global user_db

    if request.method == "POST":
        data=dict(request.json)
        checks=acount_data_checks(data)
        if checks != True:
            return (checks)

        elif sorted(['url','selection','type_server','replica']) == sorted(data.keys()): #insure no extra fields have been added
            account_db[data['url']]={}
            account_db[data['url']]['primary']=primary_master
            account_db[data['url']]['secondary']=secondary_master
            account_db[data['url']]['selection']=data['selection']
            account_db[data['url']]['type_server']=data['type_server']
            account_db[data['url']]['replica']=data['replica']
            #we need to set the vlan to 0 so that generate vlan function does not get an incorrect key!
            account_db[data['url']]['vlan']=0
            vlan_id=generate_vlan_id()
            account_db[data['url']]['vlan']=vlan_id
            account_db[data['url']]['port']=(vlan_id)*1000+30000 #3x000
            account_db[data['url']]['ip']=("10.{}.0.1".format(vlan_id)) #10.x.0.1 virtual ip

            with open('cp_account_detail.json','w') as fl:
                json.dump(account_db, fl)
            cp_version+=1
            return Response(json.dumps({'success':True}), status=200, mimetype='application/json')
        else :
            return Response(json.dumps({'success':False,'content_structure_keys':"[url,selection]"}), status=400, mimetype='application/json')

    elif request.method == "GET" :
        data=dict(request.json)
        data['filename']='cp_account_detail.json'
        return (admin_request_file(data))

def acount_data_checks(data):
    #return the HTTP - json error and filename
    if 'url' not in data.keys(): #check if username field present in json
        return (Response(json.dumps({'success':False,'comment':'Need customers username'}), status=400, mimetype='application/json'))
    elif 'selection' not in data.keys(): #check if password field present in json
        return (Response(json.dumps({'success':False,'comment':'Need Correct selections'}), status=400, mimetype='application/json'))
    elif 'type_server' not in data.keys(): #check if type of server field present in json
        return (Response(json.dumps({'success':False,'comment':'Need type_server'}), status=400, mimetype='application/json'))
    elif 'replica' not in data.keys(): #check if replica field present in json
        return (Response(json.dumps({'success':False,'comment':'Need replica sets'}), status=400, mimetype='application/json'))
    else:
        return (True)

def generate_vlan_id():
    global account_db
    l=[]
    for cust in account_db.keys():
        l.append(account_db[cust]['vlan'])
    l=sorted(l)
    return (l[-1]+1)


@app.route('/account/users',methods=['GET','POST'])
#for account details username and password
def user_details():
    global cp_version
    global user_db

    if request.method == "POST":
        data=dict(request.json)
        checks=user_data_checks(data)
        if checks != True:
            return (checks)

        else:
            user_db[data['username']]={}
            user_db[data['username']]['url']=data['url']
            user_db[data['username']]['password']=data['password']
            user_db[data['username']]['owner']=data['owner']

            with open('cp_user_detail.json','w') as fl:
                json.dump(user_db, fl)
            cp_version+=1
            return Response(json.dumps({'success':True}), status=200, mimetype='application/json')

    elif request.method == "GET" :
        data=dict(request.json)
        data['filename']='cp_user_detail.json'
        return (admin_request_file(data))

def user_data_checks(data):
    #return the HTTP - json error and filename
    if 'statistics' not in data.keys(): #check if username field present in json
        return (Response(json.dumps({'success':False,'comment':'Need Statistics'}), status=400, mimetype='application/json'))
    elif 'username' not in data.keys(): #check if password field present in json
        return (Response(json.dumps({'success':False,'comment':'Need customers username'}), status=400, mimetype='application/json'))
    elif 'password' not in data.keys(): #check if password field present in json
        return (Response(json.dumps({'success':False,'comment':'Need customers password'}), status=400, mimetype='application/json'))
    elif sorted(['url','username','password','owner']) == sorted(data.keys()):
        return (Response(json.dumps({'success':False,'content_structure_keys':"['url','username','password','owner']"}), status=400, mimetype='application/json'))
    else:
        return (True)

@app.route('/cp/network',methods=['GET'])
def provide_network_details():
    global account_db
    global user_db
    data=request.json
    if sorted(['username','password']) == sorted (data.keys()):
        if data['username'] == 'admin' and data['password']== user_db['admin']['password']: # allow only admins
            customer_db={}
            for customers_url in account_db.keys(): #return only those values which the backend wants from account_db
                #restructure the system for cp backend!
                customer_db[account_db[customers_url]['ip']]={
                                        'vlan':account_db[customers_url]['vlan'],
                                        'primary':account_db[customers_url]['primary'],
                                        'secondary':account_db[customers_url]['secondary'],
                                        'selection':account_db[customers_url]['selection'],
                                        'type_server':account_db[customers_url]['type_server'],
                                        'replica':account_db[customers_url]['replica'],
                                        'port':account_db[customers_url]['port'],
                                        'url':customers_url}

            customer_db=json.dumps(customer_db)
            return Response(json.dumps({'success':True,'data':customer_db}), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'success':False,'comment':'Unauthorized Access'}), status=400, mimetype='application/json')
    else:
        return Response(json.dumps({'success':False,'content_structure_keys':"[username,password,selection]"}), status=400, mimetype='application/json')

@app.route('/cp/statistics',methods=['GET','POST'])
#for account details username and password
def statistics_collection():
    global cp_version
    global statistics_db

    if request.method == "POST":
        data=dict(request.json)
        checks=statistics_collection_check(data)
        if checks != True:
            return (checks)
        else:
            with open('cp_statistics.json','w') as fl:
                json.dump(data, fl)
            cp_version+=1
            return Response(json.dumps({'success':True}), status=200, mimetype='application/json')

    elif request.method == "GET" :
        data=dict(request.json)
        data['filename']='cp_statistics.json'
        return (admin_request_file(data))

def statistics_collection_check(data):
    #return the HTTP - json error and filename
    if 'statistics' not in data.keys(): #check if username field present in json
        return (Response(json.dumps({'success':False,'comment':'Need statistics field'}), status=400, mimetype='application/json'))
    elif 'username' not in data.keys(): #check if password field present in json
        return (Response(json.dumps({'success':False,'comment':'Need admin username'}), status=400, mimetype='application/json'))
    elif 'password' not in data.keys(): #check if password field present in json
        return (Response(json.dumps({'success':False,'comment':'Need admin password'}), status=400, mimetype='application/json'))
    elif data['username'] =='admin' and data['password'] == user_db['admin']['password']:
        return (True)
    else:
        return (False)

#cp file synch
@app.route('/synch',methods=['GET'])
def synch_list():
    data=cp_file_list()
    return Response(json.dumps({'success':True,'data':data}), status=200, mimetype='application/json')

@app.route('/synch/files',methods=['GET'])
def synch_file():
    data=dict(request.json)
    return (admin_request_file(data))

def synch_database():
    global secondary_server
    global cp_version
    global account_db
    global user_db

    while True:
        try:
            r = requests.get('http://'+secondary_server+'/api/version')
            if r.status_code == 200:
                secondary_seq_number= r.json()['cp_version']
                print ("Secondary Server sequence number: {}".format(secondary_seq_number))
                if secondary_seq_number == cp_version:
                    print ("Everything is synch... sleeping for 10 sec")
                    time.sleep (10)
                else:
                    #request for the account file:
                    account_file=requests.get('http://'+secondary_server+'/synch/files',json={'username':'admin','password':user_db['admin']['password'],'filename':'cp_account_detail.json'})
                    if account_file.status_code == 200:
                        account_file=account_file.json()
                        if 'data' in account_file.keys():
                            account_db=account_file['data']
                            with open('cp_account_detail.json','w') as fl:
                                json.dump(account_db, fl)

                        #request for the account file:
                        user_file=requests.get('http://'+secondary_server+'/synch/files',json={'username':'admin','password':user_db['admin']['password'],'filename':'cp_user_detail.json'})
                        if user_file.status_code == 200:
                            user_file=user_file.json()
                            if 'data' in user_file.keys():
                                user_db=user_file['data']
                                with open('cp_user_detail.json','w') as fl:
                                    json.dump(user_db, fl)

                            #request cp_statistics file:
                            statistics_file=requests.get('http://'+secondary_server+'/synch/files',json={'username':'admin','password':user_db['admin']['password'],'filename':'cp_statistics.json'})
                            if statistics_file.status_code == 200:
                                statistics_file=statistics_file.json()
                                if 'data' in statistics_file.keys():
                                    statistics_db=statistics_file['data']
                                    with open('cp_statistics.json','w') as fl:
                                        json.dump(statistics_db, fl)
                                        cp_version=secondary_seq_number # change in sequence number if you receive all three file

                                #getting the files missing
                                cp_files=cp_file_list()
                                server_files=requests.get('http://'+secondary_server+'/synch',json={'username':'admin','password':user_db['admin']['password']})
                                if server_files.status_code == 200:
                                    server_files=server_files.json()['data']
                                    for fls in cp_files: #those files which are already present in the system!
                                        server_files.remove(fls)
                                    if server_files != []:
                                        for fls in server_files:
                                            #get the files one by one!
                                            new_fls=requests.get('http://'+secondary_server+'/synch/files',json={'username':'admin','password':user_db['admin']['password'],'filename':fls})
                                            if new_fls.status_code == 200:
                                                new_fls=new_fls.json()
                                                if 'data' in new_fls.keys():
                                                    new_fls=new_fls['data']
                                                    with open(fls,'w') as fl:
                                                        json.dump(new_fls, fl)
                                                        print ("GOT A NEW FILE: {}".format(fls))
                                                        time.sleep(2)

            time.sleep(10) #just sleep after one complete loop of while!

        except Exception as E: # if the request is unable to follow
            #print ("Error in connecting with secondary_server:{} | {}".format(secondary_server,E))
            print ("Error in connecting with secondary_server:{}".format(secondary_server))
            time.sleep(30)


def cp_file_list():
    all_files=os.listdir("./")
    cp_files=[]
    for fls in all_files:
        if fls.startswith("cp_"):
            cp_files.append(fls)
    print (cp_files)
    return (cp_files)


def init_start():
    global cp_version
    global account_db
    global user_db
    global statistics_db

    global primary_master
    global secondary_master
    #setting the service
    cp_version=0
    cp_version_request = [
        {
        'cp_version':cp_version
        }
    ]
    #Getting the account details from the file!
    if os.path.isfile("./cp_account_detail.json"):
        with open('cp_account_detail.json','r') as fl:
            account_db = json.load(fl)
            for url in account_db.keys():
                cp_version+=1
            print (account_db)
    else:
        account_db={
            'cpnetworks':{
                    'vlan':1,
                    'primary':primary_master,
                    'secondary':secondary_master,
                    'selection':'active-active',
                    'type_server': 'differet',
                    'replica':1,
                    'port':30001,
                    'ip':'10.1.0.1'
                    }
            }
        with open('cp_account_detail.json','w') as fl:
            json.dump(account_db, fl)

    #Getting User detail from the file!
    if os.path.isfile("./cp_user_detail.json"):
        with open('cp_user_detail.json','r') as fl:
            user_db = json.load(fl)
            for users in user_db.keys():
                cp_version+=1
            print (user_db)
    else:
        user_db={
            'admin':{
                    'password':'admin',
                    'url':'cpnetworks',
                    'owner':True
                    }
            }
        with open('cp_user_detail.json','w') as fl:
            json.dump(user_db, fl)

    #getting url target hits:
    if os.path.isfile("./cp_statistics.json"):
        with open('cp_statistics.json','r') as fl:
            statistics_db = json.load(fl)
            cp_version+=1
    else:
        statistics_db={
            'statistics':{},
            'other': {}
            }
        with open('cp_statistics.json','w') as fl:
            json.dump(statistics_db, fl)

    t=threading.Thread(target=synch_database,args = ())
    t.daemon=True
    t.start()
    return ()

if __name__ == '__main__':
    primary_master='192.168.0.1'
    secondary_master='192.168.0.2'
    secondary_server="127.0.0.1:9292"
    cp_version=0
    account_db={}
    user_db={}
    statistics_db={}
    init_start()
    app.run(debug=True, host='0.0.0.0', port=9191)
