from __future__ import unicode_literals

from abenity.client import Abenity
from base64 import b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import datetime
import pprint
import binascii
from random import randint
import pytest
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
    raise ImportError("urllib quote_plus or unquote_plus cannot be imported!")


class TestClass:
    abenity_api_username = 'username'
    abenity_api_password = 'password'
    abenity_api_key = 'EP89f4pVQbEoUXc3JcT7asdktThBVR3K'

    f = open('private-key-test.txt', 'r')
    abenity_your_private_key = f.read()

    member_profile = {'creation_time': datetime.datetime.utcnow().isoformat() + 'Z',
                      'salt': 10000,
                      'send_welcome_email': 1,
                      'client_user_id': '1',
                      'email': 'john@acme.com',
                      'firstname': 'John',
                      'lastname': 'Smith',
                      'address': '2134 Main Street',
                      'city': 'Mountain View',
                      'state': 'CA',
                      'zip': '90210',
                      'country': 'US'}

    abenity = Abenity(abenity_api_username, abenity_api_password,
                      abenity_api_key, version=2, environment='sandbox',
                      timeout=10)

    def test_set_triple_des_key(self):
        self.abenity.set_triple_des_key('IoAZqZ3RCezxj7eKWeKj00mT')
        assert self.abenity._triple_des_key == 'IoAZqZ3RCezxj7eKWeKj00mT'

    def test_encrypt_payload(self):
        self.abenity.set_triple_des_key('IoAZqZ3RCezxj7eKWeKj00mT')
        payload = urlencode(self.member_profile)
        init_vector = binascii.unhexlify("41420c2d32373c3e")
        payload_encrypted = self.abenity._encrypt_payload(payload, init_vector)
        # TODO: add a better test, right now random and no easy way to override
        #       an easy function to make it not random, that I can see.
        assert payload_encrypted is not None

    def test_encrypt_cipher(self):
        self.abenity.set_triple_des_key('IoAZqZ3RCezxj7eKWeKj00mT')

        # remove RSA randomness, so can test
        def newRand(obj=None):
            return six.b('a')

        cipher = self.abenity._encrypt_cipher(rand_function=newRand)
        assert cipher == 'vDUtFs8K8pvy0db7D1EXTrUkWv5PTeldb77BBXpQN7SM521b' + \
            'INUcgbDbNc5Cn66ukeSNykeYPSAA4fzX3CGb1fuuO5stE19FP8cabJZFQL2GL' + \
            '6UrWu%2FAz6tAx06hl4R9CUSLu0ZQPwweW%2BrLKeFluvnlHIMsdzdmiybeuS' + \
            'UhucE%3Ddecode'

    def test_sign_message(self, monkeypatch):
        self.abenity.set_triple_des_key('IoAZqZ3RCezxj7eKWeKj00mT')

        # remove RSA randomness, so can test
        def mockreturn(key=None):
            keyObj = RSA.importKey(key)

            def newRand(obj=None):
                return six.b('abc')
            keyObj._randfunc = newRand
            return keyObj

        monkeypatch.setattr(self.abenity, '_generate_rsa_key', mockreturn)
        dummy_encrypted_payload = "asdf09asdf8a0s8df0a8sd09f8a0s98df0as8df09ad"
        cipher = self.abenity._sign_message(dummy_encrypted_payload,
                                            self.abenity_your_private_key)
        assert cipher == 'LL6DS2gEQxwYUjxfNQZdKOtv1MSP7bpK0PP9LdQ%2FYG3pF' + \
            '1Sy2e2LYxkZt6M9HidkXMKc3F73gVsiBomj91YRAlKV23VNMY31wNeMmISVi' + \
            'jk24vmbNttI6Pqy6In0kOtqUgVGCJDWSMPC2P7RWL655J%2FE7QF7f0MizF5' + \
            '3Gk3DoSgx7PuNigz9YYPDe%2BSOcIpdAUOYaeJ8ahMje8cij0uOi0%2FORPr' + \
            'jvb9t4RSvO2%2FKilY%2BDn2QvMFH79l91BsZ8EpCNxgnhSAiYQXuCTnd32W' + \
            'fTWLfKvj4smxtk9TbiCIueiM9DmtIU1np8OVruu%2FFwNxnHwD09ssL8fYz1' + \
            'PLfkE%2BJhw%3D%3Ddecode'

    def test_request_data(self):
        self.abenity.set_triple_des_key('IoAZqZ3RCezxj7eKWeKj00mT')
        payload = urlencode(self.member_profile)
        init_vector = binascii.unhexlify("41420c2d32373c3e")
        iv_urlencoded = quote_plus(b64encode(init_vector).decode("utf-8")) + \
            "decode"
