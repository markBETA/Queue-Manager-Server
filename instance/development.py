"""
Development config file of the Flask App.
"""

from .config import Config as _Config


class Config(_Config):
    with open("keys/jwt.key.pub", "r") as f:
        JWT_PUBLIC_KEY = f.read()
