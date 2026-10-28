
from firebase_admin import firestore

db = firestore.client()

def get_quiz_results(user_id):
    """
    Retrieve quiz results from Firestore for a specific user.
    """
    doc_ref = db.collection("quiz_results").document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return None  # No quiz results found

import firebase_admin
from firebase_admin import credentials, firestore

# 🔥 Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with your Firebase JSON
    firebase_admin.initialize_app(cred)

db = firestore.client()

def update_quiz_results(user_id, update_data):
    """
    Update a user's quiz_results document in Firestore.
    """
    try:
        doc_ref = db.collection("quiz_results").document(user_id)
        
        # 🔹 Merge update data with existing data (does not overwrite entire document)
        doc_ref.set(update_data, merge=True)

        return True  # ✅ Success
    except Exception as e:
        print(f"❌ Error updating Firestore: {e}")
        return False  # ❌ Failure
