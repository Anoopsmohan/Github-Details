"""Compatibility alias for the removed async App Engine email backend."""
from .default import EmailBackend

__all__ = ["EmailBackend"]
