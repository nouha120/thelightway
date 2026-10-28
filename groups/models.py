from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)  # اسم المجموعة
    description = models.TextField(blank=True, null=True)  # وصف المجموعة
    admin_uid = models.CharField(max_length=255)  # مشرف المجموعة (UID من Firebase)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    member_uid = models.CharField(max_length=255)  # UID المستخدم من Firebase
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'member_uid')  # ✅ منع المستخدم من الانضمام لنفس المجموعة أكثر من مرة

    def __str__(self):
        return f"{self.member_uid} in {self.group.name}"


from django.db import models

class GroupInvitation(models.Model):
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="invitations")
    sender_uid = models.CharField(max_length=255)  # UID المرسل للدعوة (المشرف أو عضو بالمجموعة)
    receiver_uid = models.CharField(max_length=255)  # UID المستقبل للدعوة
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'receiver_uid')  # ✅ منع إرسال أكثر من دعوة لنفس الشخص داخل نفس المجموعة

    def __str__(self):
        return f"Invitation from {self.sender_uid} to {self.receiver_uid} for {self.group.name}"
