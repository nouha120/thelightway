import datetime
from firebase_admin import firestore
from backend_thelightway.settings import firestore_db
from tasks.notifications import send_push_notification

def check_and_send_reminders():
    now = datetime.datetime.utcnow()

    tasks = firestore_db.collection("tasks") \
        .where("reminder_time", "<=", now) \
        .where("status", "==", "pending") \
        .stream()

    for task in tasks:
        task_data = task.to_dict()
        user_ref = firestore_db.collection("users").document(task_data["user_id"])
        user_data = user_ref.get().to_dict()
        fcm_token = user_data.get("fcm_token")

        # ✅ التحقق إذا تم إرسال إشعار سابقاً
        last_sent = task_data.get("last_reminder_sent_at")

        send_now = False
        if last_sent is None:
            send_now = True
        else:
            last_sent_dt = last_sent.replace(tzinfo=None)  # إزالة timezone
            if (now - last_sent_dt).total_seconds() >= 15 * 60:
                send_now = True

        if send_now and fcm_token:
            send_push_notification(fcm_token, "Task Reminder", f"Don't forget: {task_data['title']} 📅")

            # ✅ تحديث الوقت الأخير للإرسال
            task.reference.update({
                "last_reminder_sent_at": firestore.SERVER_TIMESTAMP
            })

