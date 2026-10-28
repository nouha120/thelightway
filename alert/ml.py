import pandas as pd
from sklearn.ensemble import IsolationForest
import firebase_admin
from firebase_admin import credentials, firestore

# Connexion Firebase

db = firestore.client()

def detect_new_risky_zones():
    """Détecte automatiquement les nouvelles zones à risque"""
    users_locations = db.collection("user_movements").stream()
    
    data = []
    for location in users_locations:
        loc = location.to_dict()
        data.append([loc["latitude"], loc["longitude"]])
    
    df = pd.DataFrame(data, columns=["latitude", "longitude"])
    
    # Isolation Forest pour détecter les anomalies
    model = IsolationForest(contamination=0.02)
    df["anomaly"] = model.fit_predict(df)

    # Stocker les nouvelles zones à risque
    risky_places = df[df["anomaly"] == -1]
    for _, row in risky_places.iterrows():
        db.collection("danger_zones").add({
            "name": "Zone suspecte",
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "risk_level": 2
        })
    
    return "Nouvelles zones ajoutées"
