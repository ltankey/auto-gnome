from envparse import env
from dotenv import load_dotenv, find_dotenv

# Load our .env file
load_dotenv(find_dotenv())

# Load our conf
DEBUG = env.bool('DEBUG', default=False)
GITHUB_USER = env('GITHUB_USER')
GITHUB_PSX = env('GITHUB_PSX')

# FIXME: replace with persisted data somewhere
SCHEDULED_REPO_NAMES = env('SCHEDULED_REPO_NAMES')