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
    'script-src': f"'nonce-{CSP_NONCE}' 'strict-dynamic' 'unsafe-inline' https: http:",
    'report-uri': '/csp/',
    'report-to': 'csp-endpoint'
}

REPORT_TO_HEADER = {
    'group': 'csp-endpoint',
    'max-age': 10886400,
    'endpoints': ['/csp/'],
}

NON_XSRF_PROTECTED_METHODS = ('options', 'head', 'get')
XSRF_TIME_LIMIT = 86400

SECRET_KEY = os.urandom(64)

AUTH_TEMPLATE_FOLDER = os.path.join(
    os.path.dirname(__file__), 'contrib/users/templates'
)

CLOUD_TASKS_BODY = {
    'app_engine_http_request': {  # Specify the type of request.
        'http_method': 'POST',
        'app_engine_routing': {
            'version': os.getenv('GAE_VERSION', 'default')
        },
        'headers': {
            'Content-Type': 'application/json'
        }
    }
}
