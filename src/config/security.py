"""The local routes of Dreamina Settings: their paths, the requests they accept, and the replies they send."""

# The local routes of Dreamina Settings: its status, the request limits, sign-in and sign-out, and the CLI install.
ROUTES = {
    'STATUS': '/dreamina/v1/status',
    'SETTINGS': '/dreamina/v1/settings',
    'SESSION': '/dreamina/v1/session',
    'CLI': '/dreamina/v1/cli',
}

# A private route answers only a direct connection to one of these loopback hosts.
LOCAL_HOSTS = ('localhost', '127.0.0.1', '::1')

# The port a URL without one uses, for checking that a request comes to the server's own port.
DEFAULT_PORTS = {
    'HTTP': 80,
    'HTTPS': 443,
}

# Proxy metadata means the connection is not direct, so the extension refuses a request that carries it.
PROXY_HEADERS = ('forwarded', 'x-real-ip')

# Every header under this prefix is proxy metadata too.
PROXY_HEADER_PREFIX = 'x-forwarded-'

# A fetch from another site is not Dreamina Settings, so the extension refuses a change it sends.
CROSS_SITE_FETCHES = ('cross-site', 'same-site')

# Dreamina Settings sends this header with every change; a plain form or link cannot.
CHANGE_HEADER = 'X-Dreamina-Comfy'

# Every reply is JSON.
JSON_MEDIA_TYPE = 'application/json'

# Browsers neither cache a reply nor reinterpret its type.
PRIVATE_HEADERS = {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'}

# The extension refuses any JSON it reads beyond this size and depth.
JSON_LIMITS = {
    'MAX_BYTES': 1_048_576,
    'MAX_DEPTH': 16,
}

# The bytes of the random key, made once per process, that turns the account ID into ComfyUI's cache token.
ACCOUNT_TOKEN_BYTES = 16

__all__ = [
    'ACCOUNT_TOKEN_BYTES',
    'CHANGE_HEADER',
    'CROSS_SITE_FETCHES',
    'DEFAULT_PORTS',
    'JSON_LIMITS',
    'JSON_MEDIA_TYPE',
    'LOCAL_HOSTS',
    'PRIVATE_HEADERS',
    'PROXY_HEADERS',
    'PROXY_HEADER_PREFIX',
    'ROUTES',
]
