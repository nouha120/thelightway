from django.urls import path
from .views import AddReactionView, CommentDetailView, CommentListCreateView, CommunityListCreateView, DeleteReactionView, FollowUserView, FollowerFollowingCountView, FollowersListView, FollowingListView, LikePostView, MarkNotificationAsReadView, NotificationListView, PostCommentCountView, PostDetailView , PostLikeCountView, PostListCreateView, PostReactionsView, UnreadNotificationCountView, UserPostCountView

urlpatterns = [
    path("communities/", CommunityListCreateView.as_view(), name="communities"),
    path("posts/", PostListCreateView.as_view(), name="posts"),
    path("posts/count/<str:firebase_uid>/", UserPostCountView.as_view(), name="post-count"),
    path("comments/<int:post_id>/", CommentListCreateView.as_view(), name="comments-list"),
    path("comments/", CommentListCreateView.as_view(), name="comments-create"),
    path("comments/delete/<int:comment_id>/", CommentDetailView.as_view(), name="comments-delete"),
    path("comments/count/<int:post_id>/", PostCommentCountView.as_view(), name="comments-count"),
    path("reactions/", AddReactionView.as_view(), name="add-reaction"),
    path("reactions/<int:post_id>/", PostReactionsView.as_view(), name="get-reactions"),
    path("likes/", LikePostView.as_view(), name="likes"),
    path("likes/count/<int:post_id>/", PostLikeCountView.as_view(), name="likes-count"),
    path("notifications/<str:firebase_uid>/", NotificationListView.as_view(), name="notifications"),
    path("notifications/read/<int:notification_id>/", MarkNotificationAsReadView.as_view(), name="mark-notification-read"),
    path("follow/", FollowUserView.as_view(), name="follow-user"),
    path("followers/<str:firebase_uid>/", FollowersListView.as_view(), name="followers-list"),
    path("following/<str:firebase_uid>/", FollowingListView.as_view(), name="following-list"),
    path("follow/count/<str:firebase_uid>/", FollowerFollowingCountView.as_view(), name="follow-count"),
    path("reactions/delete/", DeleteReactionView.as_view(), name="delete-reaction"),
    path("notifications/unread-count/<str:firebase_uid>/", UnreadNotificationCountView.as_view(), name="unread-notification-count"),
    path("postes/<int:post_id>/", PostDetailView.as_view(), name="post-detail"),

]
