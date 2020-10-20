import datetime
import json
import urllib.parse

import requests


class Netsapiens:
    name = 'Netsapiens'
    SUPERUSER = "apiuser.maxcall@pressone.net"
    PASSWORD = "mh3zC&c58z%w8BHa"
    CLIENTID = "ResellerCallCount"
    CLIENTSECRET = "83ed3c8fad59e14de4385490a7bf32d4"

    access_token = ""
    refresh_token = ""
    token_type = ""
    expires_in = 0
    expires_time = None

    def get_access_token(self):
        token_url = "https://ucportal.pressone.net/ns-api/oauth2/token/?grant_type=%s&client_id=%s&client_secret=%s&username=%s&password=%s" % (
            'password', urllib.parse.quote(self.CLIENTID), urllib.parse.quote(self.CLIENTSECRET),
            urllib.parse.quote(self.SUPERUSER),
            urllib.parse.quote(self.PASSWORD))
        token_response = requests.post(url=token_url)
        if token_response.status_code == 200:
            token_json = token_response.json()
            self.access_token = token_json['access_token']
            self.token_type = token_json['token_type']
            self.refresh_token = token_json['refresh_token']
            self.expires_in = token_json['expires_in']
            self.expires_time = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_in)

    def refresh_token(self):
        refresh_url = "https://ucportal.pressone.net/ns-api/oauth2/token/?grant_type=refresh_token&refresh_token=%s&client_id=%s&client_secret=%s" % (
            urllib.parse.quote(self.refresh_token), urllib.parse.quote(self.CLIENTID),
            urllib.parse.quote(self.CLIENTSECRET))
        refresh_response = requests.post(url=refresh_url)
        if refresh_response.status_code == 200:
            refresh_json = refresh_response.json()
            self.access_token = refresh_json['access_token']
            self.token_type = refresh_json['token_type']
            self.refresh_token = refresh_json['refresh_token']
            self.expires_in = refresh_json['expires_in']
            self.expires_time = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_in)

    def reseller_read(self):
        try:
            if self.expires_time is None or self.expires_time <= datetime.datetime.now():
                if self.access_token == "":
                    self.get_access_token()
                else:
                    self.refresh_token()
            url = 'https://ucportal.pressone.net/ns-api/?object=reseller&action=read&format=json'
            response = requests.post(url=url, headers={'Authorization': self.token_type + ' ' + self.access_token})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(e)
            return None
