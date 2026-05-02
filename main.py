"""Compatibility entry point for platforms expecting a module-level app."""
from wsgi import application as app

application = app
