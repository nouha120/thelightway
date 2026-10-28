from django.urls import path
from .views import GroupListCreateView, JoinGroupView, GroupMembersView, PendingInvitationsView, RespondToInvitationView, SendGroupInvitationView

urlpatterns = [
    path("create/", GroupListCreateView.as_view(), name="groups"),
    path("join/", JoinGroupView.as_view(), name="join-group"),
    path("members/<int:group_id>/", GroupMembersView.as_view(), name="group-members"),
    path("invite/", SendGroupInvitationView.as_view(), name="send-invitation"),
    path("invite/respond/<int:invitation_id>/", RespondToInvitationView.as_view(), name="respond-invitation"),
    path("invite/pending/<str:firebase_uid>/", PendingInvitationsView.as_view(), name="pending-invitations"),

]
