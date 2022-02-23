import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

load_dotenv()

NAME = os.environ.get("NAME")

file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)
service_file = 'firebase_private_key.json'

# Fetch the service account key JSON file contents
cred = credentials.Certificate('%s/%s' % (dir_path, service_file))


def initialize():
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://%s.firebaseio.com' % NAME
    })
