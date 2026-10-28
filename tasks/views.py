from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import requests
from backend_thelightway.settings import firestore_db as db
from firebase_admin import firestore
from datetime import datetime, timezone
from tasks.notifications import send_push_notification

@csrf_exempt
def create_task(request):
    """Create a task with detailed fields in Firestore"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            required_fields = ["user_id", "title","notes", "date", "startTime", "endTime"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                return JsonResponse({"error": f"Missing fields: {missing}"}, status=400)

            reminder_time = None
            if data.get("reminder_time"):
               
                reminder_time = datetime.fromisoformat(data["reminder_time"]).replace(tzinfo=timezone.utc)

            task_data = {
                "user_id": data["user_id"],
                "title": data["title"],
                "notes": data["notes"],
                "date": data["date"],
                "startTime": data["startTime"],
                "endTime": data["endTime"],
                "isAllDay": data.get("isAllDay", False),
                "duration": data.get("duration", 0),
                "repeat": data.get("repeat", "once"),
                "customRepeat": data.get("customRepeat", []),
                "taskColor": data.get("taskColor", "#7D6BE3"),
                "reward_points": data.get("reward_points", 10),
                "status": "pending",
                "created_at": firestore.SERVER_TIMESTAMP,
                "reminder_time": reminder_time,
                "last_reminder_sent_at": None,
            }

            task_ref = db.collection("tasks").add(task_data)
            # ✅ Send Notification
            send_push_notification(data["user_id"], f"New Task Created: {data['title']}", "Don't forget your task!")
            return JsonResponse({
                "message": "Task created successfully",
                "task_id": task_ref[1].id
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def complete_task(request, task_id):
    if request.method == "PATCH":
        try:
            task_ref = db.collection("tasks").document(task_id)
            task_doc = task_ref.get()
            if not task_doc.exists:
                return JsonResponse({"error": "Task not found"}, status=404)

            task_data = task_doc.to_dict()
            if task_data["status"] == "completed":
                return JsonResponse({"error": "Already completed"}, status=400)

            task_ref.update({"status": "completed"})

            user_ref = db.collection("users").document(task_data["user_id"])
            user_doc = user_ref.get()

            if not user_doc.exists:
                # Create user if doesn't exist
                user_ref.set({
                    "reward_points": 10,
                    "tasks_completed_today": 1,
                })
                total_points = 10
                tasks_completed_today = 1
            else:
                user_data = user_doc.to_dict()

                today = datetime.now().strftime('%Y-%m-%d')
                task_date = task_data.get("date", today)

                if task_date == today:
                    user_ref.update({
                        "reward_points": firestore.Increment(10),
                        "tasks_completed_today": firestore.Increment(1)
                    })
                    tasks_completed_today = user_data.get("tasks_completed_today", 0) + 1
                else:
                    user_ref.update({
                        "reward_points": firestore.Increment(10),
                    })
                    tasks_completed_today = user_data.get("tasks_completed_today", 0)

                total_points = user_data.get("reward_points", 0) + 10

            return JsonResponse({
                "message": "Task completed, 10 points added",
                "total_points": total_points,
                "tasks_completed_today": tasks_completed_today
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def incomplete_task(request, task_id):
    if request.method == "PATCH":
        try:
            task_ref = db.collection("tasks").document(task_id)
            task_doc = task_ref.get()
            if not task_doc.exists:
                return JsonResponse({"error": "Task not found"}, status=404)

            task_data = task_doc.to_dict()
            if task_data["status"] == "incompleted":
                return JsonResponse({"error": "Already marked incomplete"}, status=400)

            task_ref.update({"status": "incompleted"})

            user_ref = db.collection("users").document(task_data["user_id"])
            user_doc = user_ref.get()

            if not user_doc.exists:
                # Create user with negative points if doesn't exist
                user_ref.set({
                    "reward_points": -10,
                    "tasks_completed_today": 0,
                })
                total_points = -10
                tasks_completed_today = 0
            else:
                user_data = user_doc.to_dict()
                user_ref.update({
                    "reward_points": firestore.Increment(-10),
                })

                total_points = user_data.get("reward_points", 0) - 10
                tasks_completed_today = user_data.get("tasks_completed_today", 0)

            return JsonResponse({
                "message": "Task marked incomplete, 10 points subtracted",
                "total_points": total_points,
                "tasks_completed_today": tasks_completed_today
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def delete_task(request, task_id):
    """Delete a task from Firestore"""
    if request.method == "DELETE":
        try:
            task_ref = db.collection("tasks").document(task_id)
            task_doc = task_ref.get()

            if not task_doc.exists:
                return JsonResponse({"error": "Task not found"}, status=404)

            # Delete the task from Firestore
            task_ref.delete()

            return JsonResponse({"message": "Task deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def update_task(request, task_id):
    """Update task details in Firestore"""
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)

            task_ref = db.collection("tasks").document(task_id)
            task_doc = task_ref.get()

            if not task_doc.exists:  # ✅ FIXED HERE (removed `()`)
                return JsonResponse({"error": "Task not found"}, status=404)

            update_fields = {key: value for key, value in data.items() if value is not None}
            task_ref.update(update_fields)

            return JsonResponse({"message": "Task updated successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def get_task_colors(request):
    """Returns a predefined list of task colors"""
    if request.method == "GET":
        task_colors = [
            "#Accfff",  # LIGHTBlue
            "#FFB9CE",  # LIGHTPINK
            "#dff2ff",  # lightblue
            "#959ecc",  # lightgrey
            "#d1f2eb",  # lightgreen
            "#d2b4de",  # lightpurple
            "#fae5d3",  # lightOrange
            "#d5d8d6",  # lightgray
            "#f5b7b1",  # Light Gray
            "#e7c8a0",  # sunset
        ]
        return JsonResponse({"task_colors": task_colors}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)

from django.http import JsonResponse
from firebase_admin import firestore

db = firestore.client()

def get_tasks(request):
    """استرجاع المهام الخاصة بمستخدم معين"""
    user_id = request.GET.get("user_id")  # نأخذ UID من الـ frontend

    if not user_id:
        return JsonResponse({"error": "user_id is required"}, status=400)

    try:
        # استعلام Firestore: المهام التي تخص هذا المستخدم فقط
        tasks_query = db.collection("tasks").where("user_id", "==", user_id).stream()

        tasks = []
        for doc in tasks_query:
            task = doc.to_dict()
            task["id"] = doc.id
            tasks.append(task)

        return JsonResponse({"tasks": tasks}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def verify_and_complete_task(request, task_id):
    if request.method == "POST":
        try:
            task_ref = db.collection("tasks").document(task_id)
            task_doc = task_ref.get()
            if not task_doc.exists:
                return JsonResponse({"error": "Task not found"}, status=404)

            task_data = task_doc.to_dict()
            user_phrase = request.POST.get("user_phrase", "")

            if 'file' not in request.FILES:
                return JsonResponse({"error": "No image uploaded"}, status=400)

            image_file = request.FILES["file"]
            image_bytes = image_file.read()

            # Envoi vers API IA
            detect_response = requests.post("http://127.0.0.1:8010/detect", files={"file": image_bytes})
            detect_json = detect_response.json()
            description = detect_json.get("description", "")

            compare_payload = {
                "phrase": user_phrase,
                "description": description
            }
            compare_response = requests.post("http://127.0.0.1:8001/compare", json=compare_payload)
            compare_json = compare_response.json()
            similarity = compare_json.get("similarity_score", 0)

            # ✅ قرار النجاح أو الفشل
            if similarity > 0.2:
                task_ref.update({"status": "completed"})
                return JsonResponse({
                    "message": "Task completed",
                    "similarity": similarity
                }, status=200)
            else:
                return JsonResponse({
                    "message": "Image not related to the task",
                    "similarity": similarity
                }, status=403)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)  
