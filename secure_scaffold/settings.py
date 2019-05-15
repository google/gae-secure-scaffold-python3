import base64
import os


NONCE_LENGTH = 10


def generate_nonce() -> str:
    """
    Generate a nonce for CSP purposes.

    Python URL Safe base64 encoding adds "=" as padding
    to the text - this is unsafe for CSP purposes so we strip
    it out.
    """
    b64_str = base64.urlsafe_b64encode(os.urandom(NONCE_LENGTH))
    return b64_str.decode().rstrip('=')


CSP_NONCE = generate_nonce()

CSP_CONFIG = {
    'base-uri': "'self'",
    'object-src': "'none'",
    'script-src': f"nonce-{CSP_NONCE} strict dynamic 'unsafe-inline' https: http:",
    'report-uri': '/csp/',
}

NON_XSRF_PROTECTED_METHODS = ('options', 'head', 'get')
XSRF_TIME_LIMIT = 86400

SECRET_KEY = os.urandom(64)
