import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from db import NAME

# Fetch the service account key JSON file contents
cred = credentials.Certificate("./firebase_private_key.json")\

# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://%s.firebaseio.com'%NAME
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('restricted_access/secret_document')
print(ref.get())

