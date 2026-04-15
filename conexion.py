from app.core.firebase import get_firestore_client


if __name__ == "__main__":
    db = get_firestore_client()
    print("Conexion exitosa con Firebase:", db)
