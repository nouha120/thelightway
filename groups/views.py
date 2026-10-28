
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from firebase_admin import auth
from .models import Group, GroupMember,GroupInvitation
from .serializers import GroupInvitationSerializer, GroupSerializer, GroupMemberSerializer

class GroupListCreateView(APIView):
    def post(self, request):
        admin_uid = request.data.get("admin_uid")  # UID المشرف
        name = request.data.get("name")
        description = request.data.get("description")

        if not admin_uid or not name:
            return Response({"error": "admin_uid and name are required"}, status=400)

        try:
            # ✅ تحقق من UID عبر Firebase
            user = auth.get_user(admin_uid)

            # ✅ إنشاء مجموعة جديدة
            group = Group.objects.create(admin_uid=admin_uid, name=name, description=description)
            return Response(GroupSerializer(group).data, status=201)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class JoinGroupView(APIView):
    def post(self, request):
        member_uid = request.data.get("member_uid")
        group_id = request.data.get("group_id")

        if not member_uid or not group_id:
            return Response({"error": "member_uid and group_id are required"}, status=400)

        try:
            # ✅ تحقق من UID عبر Firebase
            user = auth.get_user(member_uid)

            # ✅ تحقق مما إذا كان المستخدم عضوًا بالفعل
            group = get_object_or_404(Group, id=group_id)
            membership, created = GroupMember.objects.get_or_create(group=group, member_uid=member_uid)

            if created:
                return Response({"message": "Joined the group successfully!"}, status=201)
            else:
                return Response({"message": "You are already a member of this group."}, status=200)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class GroupMembersView(APIView):
    def get(self, request, group_id):
        members = GroupMember.objects.filter(group_id=group_id).values_list("member_uid", flat=True)
        return Response({"group_id": group_id, "members": list(members)})

class SendGroupInvitationView(APIView):
    def post(self, request):
        sender_uid = request.data.get("sender_uid")  # المرسل
        receiver_uid = request.data.get("receiver_uid")  # المستقبل
        group_id = request.data.get("group_id")  # المجموعة

        if not sender_uid or not receiver_uid or not group_id:
            return Response({"error": "sender_uid, receiver_uid, and group_id are required"}, status=400)

        if sender_uid == receiver_uid:
            return Response({"error": "You cannot invite yourself"}, status=400)

        try:
            # ✅ تحقق من صحة المستخدمين عبر Firebase
            auth.get_user(sender_uid)
            auth.get_user(receiver_uid)

            group = get_object_or_404(Group, id=group_id)

            # ✅ تحقق مما إذا كانت الدعوة موجودة مسبقًا
            invitation, created = GroupInvitation.objects.get_or_create(
                group=group,
                sender_uid=sender_uid,
                receiver_uid=receiver_uid,
                defaults={'status': 'pending'}
            )

            if created:
                return Response({"message": "Invitation sent successfully!"}, status=201)
            else:
                return Response({"message": "An invitation has already been sent to this user."}, status=200)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class RespondToInvitationView(APIView):
    def post(self, request, invitation_id):
        response = request.data.get("response")  # يجب أن يكون 'accepted' أو 'declined'

        if response not in ['accepted', 'declined']:
            return Response({"error": "Invalid response. Must be 'accepted' or 'declined'."}, status=400)

        try:
            invitation = get_object_or_404(GroupInvitation, id=invitation_id)

            if invitation.status != "pending":
                return Response({"error": "This invitation has already been processed."}, status=400)

            # ✅ تحديث حالة الدعوة
            invitation.status = response
            invitation.save()

            if response == "accepted":
                # ✅ إضافة المستخدم إلى المجموعة عند قبول الدعوة
                GroupMember.objects.create(group=invitation.group, member_uid=invitation.receiver_uid)
                return Response({"message": "Invitation accepted, and user added to the group!"}, status=200)
            else:
                return Response({"message": "Invitation declined."}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PendingInvitationsView(APIView):
    def get(self, request, firebase_uid):
        invitations = GroupInvitation.objects.filter(receiver_uid=firebase_uid, status="pending").order_by("-created_at")
        serializer = GroupInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
