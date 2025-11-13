# Copyright 2025 Community Calendar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# Flask application settings

import os

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# CSP Configuration for FullCalendar and external resources
CSP_POLICY = {
    "default-src": "'self'",
    "script-src": [
        "'self'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
    ],
    "style-src": [
        "'self'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
    ],
    "img-src": [
        "'self'",
        "data:",
        "blob:",
    ],
    "font-src": [
        "'self'",
        "https://cdnjs.cloudflare.com",
    ],
    "connect-src": "'self'",
}

CSP_POLICY_NONCE_IN = ["script-src", "style-src"]

# Session configuration
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# File upload configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
