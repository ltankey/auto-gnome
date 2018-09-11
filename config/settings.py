# Load our conf
from . import Env

env = Env()

DEBUG = env('DEBUG', default=False, cast=bool)
GITHUB_USER = env('GITHUB_USER')
GITHUB_PSX = env('GITHUB_PSX')
