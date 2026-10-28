from rest_framework.decorators import api_view
from rest_framework.response import Response
from medical.models import MedicalRecord
from users.models import User

@api_view(['POST'])
def save_medical_record(request):
    try:
        data = request.data
        firebase_uid = data.get("firebase_uid")

        user = User.objects.get(firebase_uid=firebase_uid)

        record, created = MedicalRecord.objects.update_or_create(
            user=user,
            defaults={
                "firstname": data.get("firstname"),
                "middlename": data.get("middlename"),
                "lastname": data.get("lastname"),
                "birthdate": data.get("birthdate"),
                "phone_number": data.get("phone_number"),
                "email": data.get("email"),
                "gender": data.get("gender"),
                "address": data.get("address"),
                "city": data.get("city"),
                "state": data.get("state"),
                "zip_code": data.get("zip_code"),

                "emergency_name": data.get("emergency_name"),
                "emergency_relation": data.get("emergency_relation"),
                "emergency_phone": data.get("emergency_phone"),

                "primary_substance": data.get("primary_substance"),
                "substance_specify": data.get("substance_specify"),
                "age_first_use": data.get("age_first_use"),
                "frequency_of_use": data.get("frequency_of_use"),
                "last_use_date": data.get("last_use_date"),
                "previous_treatment": data.get("previous_treatment"),

                "medical_conditions": data.get("medical_conditions"),
                "medications": data.get("medications"),
                "mental_health_history": data.get("mental_health_history"),
                "mental_health_specify": data.get("mental_health_specify"),
                "allergies": data.get("allergies"),

                "legal_issues": data.get("legal_issues"),
                "legal_issues_explain": data.get("legal_issues_explain"),

                "employment_status": data.get("employment_status"),
                "living_situation": data.get("living_situation"),
            }
        )

        return Response({"success": True, "created": created})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
