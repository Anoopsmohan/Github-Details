"""Django email backend compatibility for old settings imports.

The original project used Google App Engine's Python 2 mail API. Modern
deployments should configure Django's standard email backends directly.
"""
from django.core.mail.backends.console import EmailBackend
