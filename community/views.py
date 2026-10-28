import json
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Community, Notification, Post, Comment,Like,Follow, Reaction
from .serializers import CommunitySerializer, NotificationSerializer, PostSerializer,CommentSerializer,FollowSerializer
from firebase_admin import auth
from django.shortcuts import get_object_or_404
from firebase_admin import firestore

class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.AllowAny]  # لا حاجة إلى تسجيل دخول
    
class PostListCreateView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")

        if not firebase_uid:
            return Response({"error": "No UID provided"}, status=400)

        try:
            user = auth.get_user(firebase_uid)

            data = {
                "firebase_uid": user.uid,
                "community": request.data.get("community"),
                "content": request.data.get("content"),
            }
            serializer = PostSerializer(data=data)
            if serializer.is_valid():
                post = serializer.save()

                # ✅ جلب كل المتابعين لهذا المستخدم
                followers = Follow.objects.filter(following_uid=firebase_uid).values_list('follower_uid', flat=True)

                # ✅ جلب اسم المستخدم من Firestore
                user_doc = firestore.client().collection("users").document(firebase_uid).get()
                username = user_doc.to_dict().get("username", "Someone")

                # ✅ إرسال إشعار لكل متابع
                for follower_uid in followers:
                    Notification.objects.create(
                        firebase_uid=follower_uid,
                        sender_uid=firebase_uid,
                        post=post,
                        message=f"{username} added a new post."
                    )

                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        post_list = []

        for post in posts:
            # جلب بيانات المستخدم من Firestore عبر UID
            user_doc = firestore.client().collection("users").document(post.firebase_uid).get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                username = user_data.get("username", "Unknown")
                avatar = user_data.get("avatar", "")
            else:
                username = "Unknown"
                avatar = ""

            post_list.append({
                "id": post.id,
                "firebase_uid": post.firebase_uid,
                "username": username,
                "avatar": avatar,
                "content": post.content,
                "created_at": post.created_at.strftime("%d %b %Y"),
                # أضف هذه إذا كانت الإعجابات/التعليقات موجودة
                "likes": post.likes.count() if hasattr(post, "likes") else 0,
                "comments_count": post.comments.count() if hasattr(post, "comments") else 0,
            })

        return Response(post_list, status=200)
    def delete(self, request):
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post_id")

        if not firebase_uid or not post_id:
            return Response({"error": "firebase_uid and post_id are required"}, status=400)

        try:
            post = get_object_or_404(Post, id=post_id)

            if post.firebase_uid != firebase_uid:
                return Response({"error": "Unauthorized. This is not your post."}, status=403)

            post.delete()
            return Response({"message": "Post deleted successfully."}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
    def put(self, request):
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post_id")
        new_content = request.data.get("content")

        print("🔥 DEBUG firebase_uid =", firebase_uid)
        print("🔥 DEBUG post_id =", post_id)

        if not firebase_uid or not post_id or not new_content:
            return Response({"error": "firebase_uid, post_id, and content are required"}, status=400)

        try:
            post = get_object_or_404(Post, id=post_id)
            print("🔥 DEBUG post.firebase_uid =", post.firebase_uid)

            if post.firebase_uid != firebase_uid:
                return Response({"error": "Unauthorized: This is not your post"}, status=403)

            post.content = new_content
            post.save()

            return Response({"message": "Post updated successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class UserPostCountView(APIView):
    def get(self, request, firebase_uid):
        post_count = Post.objects.filter(firebase_uid=firebase_uid).count()  # عدد المنشورات

        return Response({
            "firebase_uid": firebase_uid,
            "post_count": post_count
        })
    

class CommentListCreateView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")  # UID المستخدم من Firebase
        post_id = request.data.get("post")  # معرف المنشور

        if not firebase_uid or not post_id:
            return Response({"error": "firebase_uid and post are required"}, status=400)

        try:
            # ✅ تحقق من UID عبر Firebase
            user = auth.get_user(firebase_uid)

            # ✅ تحقق مما إذا كان المنشور موجودًا
            post = get_object_or_404(Post, id=post_id)

            # ✅ حفظ التعليق
            data = {
                "firebase_uid": user.uid,
                "post": post.id,
                "content": request.data.get("content"),
            }
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

                # ✅ جلب معلومات المعلّق من Firestore
                user_doc = firestore.client().collection("users").document(user.uid).get()
                username = user_doc.to_dict().get("username", "Someone")
                # ✅ إرسال إشعار لصاحب المنشور
                if firebase_uid != post.firebase_uid:
                    Notification.objects.create(
                        firebase_uid=post.firebase_uid,
                        post=post,
                        sender_uid=user.uid,  # ✅ ممتاز، موجود
                        message=f"{username} commented on your post."  # ✅ بدل User {uid}
                    )

                 # ✅ إشعار للمتابعين الآخرين (باستثناء نفسه وصاحب المنشور)
                followers = Follow.objects.filter(
                    following_uid=firebase_uid
                ).exclude(follower_uid__in=[firebase_uid, post.firebase_uid]).values_list("follower_uid", flat=True)

                for follower_uid in followers:
                    Notification.objects.create(
                        firebase_uid=follower_uid,
                        sender_uid=firebase_uid,  # ✅ جيد
                        post=post,
                        message=f"{username} commented on a post."
                    )

                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    def get(self, request, post_id):
        comments = Comment.objects.filter(post=post_id).order_by("-created_at")  # جلب التعليقات بترتيب زمني
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
class CommentDetailView(APIView):
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # ✔️ Fix: parse DELETE body manually
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=400)

        if data.get("firebase_uid") != comment.firebase_uid:
            return Response({"error": "Unauthorized"}, status=403)

        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=200)

class LikePostView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post")

        if not firebase_uid or not post_id:
            return Response({"error": "firebase_uid and post are required"}, status=400)

        try:
            user = auth.get_user(firebase_uid)
            post = get_object_or_404(Post, id=post_id)

            like, created = Like.objects.get_or_create(firebase_uid=user.uid, post=post)

            if created:
                # ✅ جلب اسم المستخدم من Firestore
                user_doc = firestore.client().collection("users").document(firebase_uid).get()
                username = user_doc.to_dict().get("username", "Someone")

                Notification.objects.create(
                    firebase_uid=post.firebase_uid,
                    sender_uid=user.uid,  # ✅ مضاف
                    post=post,
                    message=f"{username} liked your post."
                )
                return Response({"message": "Post liked successfully!"}, status=201)
            else:
                return Response({"message": "You have already liked this post."}, status=200)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    def delete(self, request):
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post")

        if not firebase_uid or not post_id:
            return Response({"error": "firebase_uid and post are required"}, status=400)

        try:
            # ✅ تحقق من UID عبر Firebase
            user = auth.get_user(firebase_uid)

            # ✅ تحقق مما إذا كان المنشور موجودًا
            post = get_object_or_404(Post, id=post_id)

            # ✅ حذف الإعجاب إذا كان موجودًا
            like = Like.objects.filter(firebase_uid=user.uid, post=post)
            if like.exists():
                like.delete()
                return Response({"message": "Like removed successfully!"}, status=200)
            else:
                return Response({"error": "You have not liked this post."}, status=400)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500) 


class PostLikeCountView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like_count = Like.objects.filter(post=post).count()
        return Response({"post_id": post.id, "like_count": like_count})


class PostCommentCountView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)  # التحقق من وجود المنشور
        comment_count = Comment.objects.filter(post=post).count()  # حساب عدد التعليقات
        return Response({"post_id": post.id, "comment_count": comment_count})
    
from firebase_admin import firestore

from rest_framework.views import APIView
from rest_framework.response import Response
from firebase_admin import firestore
from .models import Notification

class NotificationListView(APIView):
    def get(self, request, firebase_uid):
        notifications = Notification.objects.filter(
            firebase_uid=firebase_uid,
            is_read=False
        ).order_by("-created_at")

        enriched = []

        for notif in notifications:
            # جلب UID المرسل
            sender_uid = notif.sender_uid
            sender_data = {}

            if sender_uid:
                # جلب بيانات المستخدم من Firestore مباشرة
                sender_doc = firestore.client().collection("users").document(sender_uid).get()
                if sender_doc.exists:
                    sender_data = sender_doc.to_dict()

            enriched.append({
                "id": notif.id,
                "message": notif.message,
                "created_at": notif.created_at.strftime("%d %b %Y %H:%M"),
                "post": notif.post.id if notif.post else None,
                "sender": {
                    "username": sender_data.get("username", "Unknown"),
                    "avatar": sender_data.get("avatar", ""),
                    "uid": sender_uid,
                }
            })

        return Response(enriched)

class MarkNotificationAsReadView(APIView):
    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."}, status=200)

class FollowUserView(APIView):
    def post(self, request):
        follower_uid = request.data.get("follower_uid")  # المستخدم الذي يتابع
        following_uid = request.data.get("following_uid")  # المستخدم الذي يتم متابعته

        if not follower_uid or not following_uid:
            return Response({"error": "Both follower_uid and following_uid are required"}, status=400)

        if follower_uid == following_uid:
            return Response({"error": "You cannot follow yourself"}, status=400)

        try:
            # ✅ تحقق من UID عبر Firebase
            auth.get_user(follower_uid)
            auth.get_user(following_uid)

            # ✅ تحقق مما إذا كان المستخدم يتابع بالفعل
            follow, created = Follow.objects.get_or_create(follower_uid=follower_uid, following_uid=following_uid)

            if created:
                # ✅ جلب اسم المتابع من Firestore
                user_doc = firestore.client().collection("users").document(follower_uid).get()
                username = user_doc.to_dict().get("username", "Someone")

                # ✅ إرسال إشعار للمستخدم الذي تمت متابعته
                Notification.objects.create(
                    firebase_uid=following_uid,
                    sender_uid=follower_uid,  # ✅ موجود
                    message=f"User {follower_uid} started following you!"
                )

                return Response({"message": "Followed successfully!"}, status=201)
            else:
                return Response({"message": "You are already following this user."}, status=200)

        except auth.UserNotFoundError:
            return Response({"error": "User not found in Firebase"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request):
        follower_uid = request.data.get("follower_uid")
        following_uid = request.data.get("following_uid")

        if not follower_uid or not following_uid:
            return Response({"error": "Both follower_uid and following_uid are required"}, status=400)

        try:
            # ✅ حذف العلاقة من قاعدة البيانات
            follow = Follow.objects.filter(follower_uid=follower_uid, following_uid=following_uid)
            if follow.exists():
                follow.delete()
                return Response({"message": "Unfollowed successfully!"}, status=200)
            else:
                return Response({"error": "You are not following this user."}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class FollowersListView(APIView):
    def get(self, request, firebase_uid):
        followers = Follow.objects.filter(following_uid=firebase_uid).values_list('follower_uid', flat=True)
        return Response({"followers": list(followers)})

class FollowingListView(APIView):
    def get(self, request, firebase_uid):
        following = Follow.objects.filter(follower_uid=firebase_uid).values_list('following_uid', flat=True)
        return Response({"following": list(following)})

class FollowerFollowingCountView(APIView):
    def get(self, request, firebase_uid):
        followers_count = Follow.objects.filter(following_uid=firebase_uid).count()  # عدد المتابعين
        following_count = Follow.objects.filter(follower_uid=firebase_uid).count()  # عدد الأشخاص الذين يتابعهم المستخدم

        return Response({
            "firebase_uid": firebase_uid,
            "followers_count": followers_count,
            "following_count": following_count
        })
# views.py
class AddReactionView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post")
        emoji = request.data.get("emoji")

        if not all([firebase_uid, post_id, emoji]):
            return Response({"error": "Missing data"}, status=400)

        # ✅ حذف أي reaction قديم لهذا المستخدم على هذا المنشور
        Reaction.objects.filter(firebase_uid=firebase_uid, post_id=post_id).delete()

        # ✅ ثم إضافة الجديد
        Reaction.objects.create(
            firebase_uid=firebase_uid,
            post_id=post_id,
            emoji=emoji
        )
         # ✅ جلب المنشور
        post = get_object_or_404(Post, id=post_id)

        # ✅ إذا لم يكن نفس الشخص، أرسل إشعار
        if post.firebase_uid != firebase_uid:
            # جلب الاسم من Firestore
            user_doc = firestore.client().collection("users").document(firebase_uid).get()
            username = user_doc.to_dict().get("username", "Someone")

            Notification.objects.create(
                firebase_uid=post.firebase_uid,  # صاحب المنشور
                sender_uid=firebase_uid,         # ✅ موجود
                post=post,
                message=f"{username} reacted to your post."
            )

        return Response({"message": "Reaction updated!"}, status=201) 
class PostReactionsView(APIView):
    def get(self, request, post_id):
        firebase_uid = request.query_params.get("firebase_uid")

        reactions = Reaction.objects.filter(post_id=post_id)
        grouped = {}

        for reaction in reactions:
            grouped[reaction.emoji] = grouped.get(reaction.emoji, 0) + 1

        user_reaction = None
        if firebase_uid:
            user_reaction_obj = reactions.filter(firebase_uid=firebase_uid).first()
            if user_reaction_obj:
                user_reaction = user_reaction_obj.emoji

        grouped["user_reaction"] = user_reaction

        return Response(grouped)

class DeleteReactionView(APIView):
    def post(self, request): # ✅ POST بدل DELETE
        firebase_uid = request.data.get("firebase_uid")
        post_id = request.data.get("post")

        if not firebase_uid or not post_id:
            return Response({"error": "Missing data"}, status=400)

        reaction = Reaction.objects.filter(firebase_uid=firebase_uid, post_id=post_id)
        if reaction.exists():
            reaction.delete()
            return Response({"message": "Reaction deleted"}, status=200)
        else:
            return Response({"message": "Reaction not found"}, status=404)


# views.py
class UnreadNotificationCountView(APIView):
    def get(self, request, firebase_uid):
        count = Notification.objects.filter(firebase_uid=firebase_uid, is_read=False).count()
        return Response({"unread_count": count})

class PostDetailView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        # جلب بيانات المستخدم من Firestore
        user_doc = firestore.client().collection("users").document(post.firebase_uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            username = user_data.get("username", "Unknown")
            avatar = user_data.get("avatar", "")
        else:
            username = "Unknown"
            avatar = ""

        return Response({
            "id": post.id,
            "firebase_uid": post.firebase_uid,
            "username": username,
            "avatar": avatar,
            "content": post.content,
            "created_at": post.created_at.strftime("%d %b %Y"),
            "likes": post.likes.count() if hasattr(post, "likes") else 0,
            "comments_count": post.comments.count() if hasattr(post, "comments") else 0,
        }, status=200)
