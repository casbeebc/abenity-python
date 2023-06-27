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
import six
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
    raise ImportError("urllib, quote_plus or unquote_plus cannot be imported!")

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

        self._public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC8NVUZU' + \
                           'tr2IHiFoY8s/qFGmZOIewAvgS4FMXWZ81Qc8lkAlZr9e1' + \
                           '71xn4PgKr+S7YsfCt+1XKyo5XmrJyaNUe/aRptB93NFn6' + \
                           'RoFzExgfpkooxcHpWcPy+Hb5e0rwPDBA6zfyrYRj8uK/1' + \
                           'HleFEr4v8u/HbnJmiFoNJ2hfZXn6Qw== phpseclib-ge' + \
                           'nerated-key'

        self._triple_des_key = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for n in range(self.des3_key_size)
            ])

    def set_triple_des_key(self, key=None):
        if key is None:
            self._triple_des_key = ''.join([
                random.choice(string.ascii_letters + string.digits)
                for n in range(self.des3_key_size)
                ])
        else:
            self._triple_des_key = key

    def _send_request(self, api_method, http_method='GET', data={}):
        params = {'api_username': self._username,
                  'api_password': self._password,
                  'api_key': self._api_key}
        params.update(data.items())

        api_url = self._api_url+'/v'+str(self._version)+'/client'+api_method
        headers = {'user-agent': 'abenity/abenity-python)'}
        response = {}

        if http_method == 'GET':
            response = requests.get(api_url, verify=False, headers=headers,
                                    params=params, timeout=self._timeout)
        elif http_method == 'POST':
            response = requests.post(api_url, verify=False, headers=headers,
                                     data=params, timeout=self._timeout)
        elif http_method == 'DELETE':
            response = requests.delete(api_url, verify=False, headers=headers,
                                     data=params, timeout=self._timeout)

        return json.loads(response.text)

    def _encrypt_payload(self, payload, iv):
        cipher = DES3.new(six.b(self._triple_des_key),
                          DES3.MODE_CBC,
                          IV=iv)

        # If the size of the data is not n * blocksize,
        # the data will be padded with '\0'.
        padding = '\0' * (self.iv_size - len(payload) % self.iv_size)
        payload_padded = payload + padding

        payload_encrypted = cipher.encrypt(six.b(payload_padded))
        payload_encrypted_base64 = b64encode(payload_encrypted).decode("utf-8")
        return quote_plus(payload_encrypted_base64) + "decode"

    def _generate_rsa_key(self, key):
        return RSA.importKey(key)

    def _encrypt_cipher(self, rand_function=None):
        key = self._generate_rsa_key(self._public_key)
        if rand_function is None:
            cipher = PKCS1_v1_5.new(key)
        else:
            cipher = PKCS1_v1_5.new(key, randfunc=rand_function)

        des3_key_bytes = six.b(self._triple_des_key)

        des3_key_encrypted = cipher.encrypt(des3_key_bytes)
        des3_key_enc_base64 = b64encode(des3_key_encrypted).decode('utf-8')
        des3_key_enc_base64_encoded = quote_plus(des3_key_enc_base64) + \
            "decode"
        return des3_key_enc_base64_encoded

    def _sign_message(self, payload_encrypted_base64_urlencoded, private_key):
        key = self._generate_rsa_key(private_key)
        signer = PKCS1_v1_5_Signature.new(key)
        payload = unquote_plus(payload_encrypted_base64_urlencoded[:-6])
        md5_hash = MD5.new(payload.encode("utf-8"))
        signature = signer.sign(md5_hash)
        signature_base64 = b64encode(signature).decode("utf-8")
        return quote_plus(signature_base64) + "decode"

    def sso_member(self, member_profile, private_key, init_vector=None):
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
        if init_vector is None:
            init_vector = Random.get_random_bytes(self.iv_size)

        iv_urlencoded = quote_plus(b64encode(init_vector).decode("utf-8")) + \
            "decode"

        payload_encrypted = self._encrypt_payload(payload, init_vector)
        encrypted_inner_key = self._encrypt_cipher()
        signature = self._sign_message(payload_encrypted, private_key)

        request_data = {
                        'Payload': unquote_plus(payload_encrypted),
                        'Cipher': unquote_plus(encrypted_inner_key),
                        'Signature': unquote_plus(signature),
                        'Iv': unquote_plus(iv_urlencoded)
                        }
        return self._send_request('/sso_member.json', 'POST', request_data)
