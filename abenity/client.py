from abenity import exceptions
import random
import string
import requests
import json


class Abenity(object):
    """
    Abenity API client
    """

    def __init__(self, username, password, api_key, version=2,
                 environment='live', timeout=10):
        """
        Constructor
        Args:
            username: API username or real username
            password: API token or user password
            api_key: API key
            version: API version
            environment: 'live' or 'sandbox'
            timeout: timeout in seconds
        """

        self._username = username
        self._password = password
        self._api_key = api_key
        self._version = int(version)
        self._environment = environment
        self._api_url = 'https://api.abenity.com'
        if environment == 'sandbox':
            self._api_url = 'https://sandbox.abenity.com'
        self._timeout = timeout

        self._public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC8NVUZUtr2I'+
        'HiFoY8s/qFGmZOIewAvgS4FMXWZ81Qc8lkAlZr9e171xn4PgKr+S7YsfCt+1XKyo5Xmr'+
        'JyaNUe/aRptB93NFn6RoFzExgfpkooxcHpWcPy+Hb5e0rwPDBA6zfyrYRj8uK/1HleFE'+
        'r4v8u/HbnJmiFoNJ2hfZXn6Qw== phpseclib-generated-key'

        self._triple_des_key = random = ''.join([random.choice(
            string.ascii_letters + string.digits) for n in range(24)])

    def _send_request(self, http_method='GET', data={}):
        params = dict('api_username': self.api_username,
                      'api_password': self.api_password,
                      'api_key': self.api_key,
                      data.items())

        api_url = self._api_url+'/v'+self._version+'/client'+http_method
        headers = {'user-agent': 'abenity/abenity-php v2)'}
        response = {}

        if http_method == 'GET':
            response = requests.get(api_url, verify=False, headers=headers
                                    params=params, timeout=self._timeout)
        elif http_method == 'POST':
            response = requests.post(api_url, verify=False, headers=headers
                                     params=params, timeout=self._timeout)

        return json.loads(response.text)









