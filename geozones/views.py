from rest_framework.decorators import api_view
from rest_framework.response import Response
from geopy.distance import geodesic
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import joblib
import os


# ✅ تحميل النموذج مرة واحدة فقط
model = None
df = None

def load_prediction_data():
    global model, df
    if model is not None and df is not None:
        return
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "rf_model.pkl")
    
    # ✅ تحميل وتنظيف البيانات مرة واحدة فقط عند بداية التشغيل
    DATASET_PATH = os.environ.get("GEOZONES_DATASET_PATH", os.path.join(os.path.dirname(__file__), "dataset.xlsx"))  # عدّل المسار حسب مكان الملف
    if not os.path.isfile(DATASET_PATH):
        raise FileNotFoundError("Geolocation dataset missing. Restore geozones/dataset.xlsx or set GEOZONES_DATASET_PATH.")
    df = pd.read_excel(DATASET_PATH)
    df = df.dropna()
    
    # 🔄 تنظيف وتحضير البيانات
    for col in ['distance_to_police_stations', 'distance_to_hospitals', 'distance_to_schools']:
        df[col] = df[col].astype(str).str.replace(' km', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ✅ تحويل sells_alcohol إلى أرقام
    df['sells_alcohol'] = df['sells_alcohol'].astype(str).str.strip().str.lower()
    df['sells_alcohol'] = df['sells_alcohol'].map({'yes': 1, 'no': 0})
    df['sells_alcohol'] = pd.to_numeric(df['sells_alcohol'], errors='coerce')
    
    # ✅ حساب ميزات إضافية ضرورية (Feature Engineering)
    reference_point = (36.8065, 10.1815)
    df['distance_to_center'] = df.apply(lambda row: geodesic((row['latitude'], row['longitude']), reference_point).km, axis=1)
    
    df['safety_score'] = (
        df['distance_to_police_stations'] * 0.5
        + df['distance_to_hospitals'] * 0.3
        + df['distance_to_schools'] * 0.2
    )
    
    df['alcohol_density'] = df.groupby('place_type')['sells_alcohol'].transform('mean')
    
    def time_to_minutes(time):
        if isinstance(time, str):
            try:
                h, m = map(int, time.split(":"))
                return h * 60 + m
            except:
                return 0
        return 0
    
    df['close_time'] = df['close_time'].apply(time_to_minutes)
    df['late_night_activity'] = df['close_time'].apply(lambda x: 1 if x > 1380 else 0)
    model = joblib.load(MODEL_PATH)
    
    # ✅ دالة استخراج الميزات من موقع المستخدم

def extract_features_from_location(lat, lon):
    load_prediction_data()
    user_location = (lat, lon)
    df['distance'] = df.apply(lambda row: geodesic((row['latitude'], row['longitude']), user_location).km, axis=1)
    closest = df.sort_values(by='distance').iloc[0]

    input_features = np.array([[
        closest['latitude'],
        closest['longitude'],
        closest['risk_score'],
        closest['security_reports'],
        closest['user_reports'],
        closest['distance_to_schools'],
        closest['distance_to_hospitals'],
        closest['distance_to_police_stations'],
        closest['close_time'],
        closest['distance_to_center'],
        closest['safety_score'],
        closest['alcohol_density'],
        closest['late_night_activity']
    ]])

    return input_features

# ✅ دالة جلب FCM token
def get_firebase_token_from_uid(uid):
    db = firestore.client()
    user_doc = db.collection("users").document(uid).get()
    if user_doc.exists:
        return user_doc.to_dict().get("fcm_token")
    return None

# ✅ دالة إرسال إشعار عبر Firebase Cloud Messaging
def send_fcm_notification(firebase_token, title, body, server_key):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": firebase_token,
        "notification": {
            "title": title,
            "body": body
        },
        "priority": "high"
    }
    requests.post(url, json=payload, headers=headers)

# ✅ الـ endpoint الرئيسي
@api_view(['POST'])
def predict_and_alert(request):
    lat = request.data.get("latitude")
    lon = request.data.get("longitude")
    uid = request.data.get("firebase_uid")

    if not all([lat, lon, uid]):
        return Response({"error": "Missing fields"}, status=400)

    try:
        features = extract_features_from_location(lat, lon)
        prediction = model.predict(features)[0]

        # 🆕 دعم جميع التصنيفات
        label = {
            0: "Safe",
            1: "Dangerous",
            2: "Suspicious"
        }.get(prediction, "Unknown") 

        return Response({
            "prediction": int(prediction),
            "label": label
        })

    except FileNotFoundError as e:
        return Response({"error": str(e)}, status=503)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
