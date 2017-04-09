from abenity import exceptions
from base64 import b64encode
from Crypto import Random
from Crypto.Cipher import DES3
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_5_Signature

import random
import string
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import sys

version = sys.version_info[0]
is_py2 = (version == 2)
is_py3 = (version == 3)

if is_py2:
    from urllib import quote_plus
    from urllib import unquote_plus
    from urllib import urlencode
elif is_py3:
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
    from urllib.parse import urlencode
else:
    raise ImportError("urllib quote_plus or unquote_plus cannot be imported!")

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Abenity(object):
    """
    Abenity API client
    """
    iv_size = 8  # initialization vector size
    des3_key_size = 24

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

        self._public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC8NVUZUt' + \
                           'r2IHiFoY8s/qFGmZOIewAvgS4FMXWZ81Qc8lkAlZr9e171' + \
                           'xn4PgKr+S7YsfCt+1XKyo5XmrJyaNUe/aRptB93NFn6RoF' + \
                           'zExgfpkooxcHpWcPy+Hb5e0rwPDBA6zfyrYRj8uK/1HleF' + \
                           'Er4v8u/HbnJmiFoNJ2hfZXn6Qw== ' + \
                           'phpseclib-generated-key'

        self._triple_des_key = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for n in range(self.des3_key_size)
            ])

    def _send_request(self, api_method, http_method='GET', data={}):
        params = {'api_username': self._username,
                  'api_password': self._password,
                  'api_key': self._api_key}
        params.update(data.items())

        api_url = self._api_url+'/v'+str(self._version)+'/client'+api_method
        headers = {'user-agent': 'abenity/abenity-php v2)'}
        response = {}

        if http_method == 'GET':
            response = requests.get(api_url, verify=False, headers=headers,
                                    params=params, timeout=self._timeout)
        elif http_method == 'POST':
            response = requests.post(api_url, verify=False, headers=headers,
                                     params=params, timeout=self._timeout)

        return json.loads(response.text)

    def _encrypt_payload(self, payload, iv):
        cipher = DES3.new(self._triple_des_key,
                          DES3.MODE_CBC,
                          IV=iv)

        # If the size of the data is not n * blocksize,
        # the data will be padded with '\0'.
        padding = '\0' * (self.iv_size - len(payload) % self.iv_size)
        payload_padded = payload + padding

        payload_encrypted = cipher.encrypt(payload_padded)
        payload_encrypted_base64 = b64encode(payload_encrypted).decode("utf-8")
        return quote_plus(payload_encrypted_base64) + "decode"

    def _encrypt_cipher(self):
        key = RSA.importKey(self._public_key)
        cipher = PKCS1_v1_5.new(key)
        des3_key_encrypted = cipher.encrypt(bytearray(self._triple_des_key,
                                                      "utf-8"))
        des3_key_enc_base64 = b64encode(des3_key_encrypted).decode("utf-8")
        return quote_plus(des3_key_enc_base64) + "decode"

    def _sign_message(self, payload_encrypted_base64_urlencoded, private_key):
        key = RSA.importKey(private_key)
        signer = PKCS1_v1_5_Signature.new(key)
        payload = unquote_plus(payload_encrypted_base64_urlencoded[:-6])
        md5_hash = MD5.new(payload.encode("utf-8"))
        signature = signer.sign(md5_hash)
        signature_base64 = b64encode(signature).decode("utf-8")
        return quote_plus(signature_base64) + "decode"

    def sso_member(self, member_profile, private_key):
        """
        Single Sign-On a member

        Args:
            member_profile: A dict of key/value pairs that describes the member
            private_key: Your RSA private key, used to sign your message

        Returns:
            The raw API response string
        """
        payload = urlencode(member_profile)

        # Create initialization vector (iv)
        init_vector = Random.new().read(self.iv_size)
        iv_urlencoded = b64encode(init_vector).decode("utf-8") + "decode"

        payload_encrypted = self._encrypt_payload(payload, init_vector)
        encrypted_inner_key = self._encrypt_cipher()
        signature = self._sign_message(payload_encrypted, private_key)

        request_data = {
                        'Payload': payload_encrypted,
                        'Cipher': encrypted_inner_key,
                        'Signature': signature,
                        'Iv': iv_urlencoded
                        }
        return self._send_request('/sso_member.json', 'POST', request_data)
