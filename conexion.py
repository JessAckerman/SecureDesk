import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(r"C:\Users\Jess\OneDrive\Desktop\SecureDesk\llaveKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

print("Conexión exitosa con Firebase")