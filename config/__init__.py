# from os import environ
from envparse import env
from .kms import string_or_b64kms


class Env(object):
    def __call__(self, var, default=None, cast=None):
        value = env(var, default=default, cast=cast)
        return string_or_b64kms(value)

# class Env(object):
#     """Wrapper around os.getenv with added AWS KMS encryption support."""

#     def __call__(self, var, default=None):
#         value = environ.get(var, default)
#         return string_or_b64kms(value)
