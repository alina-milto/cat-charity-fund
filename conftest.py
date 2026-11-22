"""Root pytest configuration: test values for required settings."""

import os


os.environ.setdefault('SECRET', 'test-secret-key-that-is-long-enough-for-jwt')
