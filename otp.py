import math, random
import smtplib
import logging
import os, json, ast
from user import UserAccount

logging.basicConfig(level=logging.INFO)

NWS_CREDS = {'email': 'nws.cp12345@gmail.com', 'password': 'Qwe12345@'}
NWS_CUSTOMER_PAGES_DIR = os.getcwd() + "/nws_urls"

class OTP():

    def __init__(self, url):
        self.url = url
        self.url_folder = NWS_CUSTOMER_PAGES_DIR + "/" + self.url
        self.otp_file = self.url_folder + "/" + "otp.json"


    def _generate_otp(self):
      digits = "0123456789"
      OTP = ""
      for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
      with open(self.otp_file, 'w') as outfile:
          outfile.write(json.dumps({"otp": OTP}))
      return OTP


    def send_email(self, user):
        user = UserAccount(user, None, None)
        user_details = user.find_details()
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(NWS_CREDS['email'], NWS_CREDS['password'])
        generated_otp = self._generate_otp()
        subject = "NWS OTP Notification"
        body = "The randomly generated OTP is : {}".format(generated_otp)
        message = 'Subject: {}\n\n{}'.format(subject, body)
        logging.info(message)
        s.sendmail(NWS_CREDS['email'], user_details['email'], message)
        s.quit()
        logging.info("Sent OTP email successfully!")
        return message

    def match_otp(self, user_otp):
        with open(self.otp_file, 'r') as infile:
            data = infile.read()
        logging.info(ast.literal_eval(data))
        otp_info = ast.literal_eval(data)
        if otp_info["otp"] == user_otp:
            return True
        else:
            return False
