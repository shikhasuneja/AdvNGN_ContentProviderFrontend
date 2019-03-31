import os
import json

class UserAccount():

    def __init__(self, username, emailid, password):
        self.username = username
        self.emailid = emailid
        self.password = password

    def create_account(self):
        userfolder = self.emailid
        credentials = {'username': self.username, 'email': self.emailid, 'password': self.password}
        if not os.path.exists(userfolder):
            os.makedirs(userfolder)
            creds = json.dumps(credentials)
            with open(userfolder + '/credentials.json', 'w') as outfile:
                outfile.write(creds)
