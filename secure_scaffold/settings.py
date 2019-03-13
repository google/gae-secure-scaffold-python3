import base64
import os


NONCE_LENGTH = 10


def generate_nonce():
    return base64.b64encode(os.urandom(NONCE_LENGTH))


CSP_CONFIG = {
    'base-uri': "'self'",
    'object-src': "'none'",
    'script-src': f"'nonce-{generate_nonce()}' 'strict dynamic' 'unsafe-inline' https: http:",
    'report-uri': '/csp/',
}
