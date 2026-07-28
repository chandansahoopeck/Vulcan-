import requests, json
# from .auto_config import cyberark_url
import base64

# windows host url
host_url = "http://uls-op-itauto01.corp.sandisk.com"
# cyberark url
cyberark_url = f"{host_url}/cyberark/v1/pwd"

class cyberark:

    def __init__(self, username) -> None:
        """
        cyberark is used to retrieve credentials from cyberark password provider
        :param username: to retrieve password from username
        """
        self.username = username
        self.url = cyberark_url
        self.headers = {
            'Authorization': 'Basic Q3liZXJBcms6U0RIM0xQTTMhU0RIM0xQTTMh',
            'Content-Type': 'application/json'
        }
        self.payload = json.dumps({
                'username': self.username
            })
 
    def get_password(self):
        """

        :return:
        """
        response =  requests.post(url=self.url, data=self.payload, headers=self.headers)
        response = response.json()
        return response['password']
 
    def get_cyberark_object(self):
       response = requests.post(url=self.url, data=self.payload, headers=self.headers)
       response = response.json()
       return response
