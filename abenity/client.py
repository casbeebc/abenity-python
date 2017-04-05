from abenity import exceptions

try:
    from urllib import request as http
except ImportError:
    import urllib2 as http


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
        if environment == 'sandbox':
            self.api_url = 'https://sandbox.abenity.com'
        self._timeout = timeout
        self._public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC8NVUZUtr2I'+
        'HiFoY8s/qFGmZOIewAvgS4FMXWZ81Qc8lkAlZr9e171xn4PgKr+S7YsfCt+1XKyo5Xmr'+
        'JyaNUe/aRptB93NFn6RoFzExgfpkooxcHpWcPy+Hb5e0rwPDBA6zfyrYRj8uK/1HleFE'+
        'r4v8u/HbnJmiFoNJ2hfZXn6Qw== phpseclib-generated-key'
