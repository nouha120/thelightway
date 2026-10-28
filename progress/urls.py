from django.urls import path

from progress.views import CompleteChallengeView, CreateChallengeView, MyChallengesView, RecoveryProgressByUIDView, RelapseView, StartChallengeView, StartRecoveryView

urlpatterns = [
    path('progress-summary/', RecoveryProgressByUIDView.as_view(), name='progress-summary'),
    path('relapse/', RelapseView.as_view(), name='relapse'),
    path('challenges/complete/', CompleteChallengeView.as_view(), name='complete-challenge'),
    path('start-recovery/', StartRecoveryView.as_view(), name='Start-recovery'),
    path('complete-challenge/', CompleteChallengeView.as_view(), name='Complete-Challenge'),
    path('start-challenge/', StartChallengeView.as_view(), name='Start-Challenge'),
    path("my-challenges/", MyChallengesView.as_view(), name="my-challenges"),
    path("challenges/create/", CreateChallengeView.as_view(), name="Create-Challenge"),
    
]
