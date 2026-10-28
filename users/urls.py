from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.view.account.enable import enable_account
from users.view.account.update import update_account

# Root view for /api/users/
@api_view(['GET'])
def users_api_root(request):
    return Response({
        'predict_relapse': '/api/users/predict-relapse/',
        'delete_account': '/api/users/delete/',
        'disable_account': '/api/users/disable/',
        'login': '/api/users/login/',
        'login_google': '/api/users/login/google/',
        'logout': '/api/users/logoutt/',
        'reset_password': '/api/users/password/reset/',
        'profile': '/api/users/profile/',
        'signup': '/api/users/signup/',
        'signup_google': '/api/users/signup/google/',
    })

from users.view.account.delete import delete_account
from users.view.account.disable import disable_account
from users.view.auth.login import login_or_register, login_with_google
from users.view.auth.logoutt import logout
from users.view.auth.password import reset_password
from users.view.auth.profile import get_user_profile, update_user_profile
from users.view.auth.signupp import signup, signup_with_google
from .views import get_relapse_prediction

urlpatterns = [
    path('', users_api_root, name='users_api_root'),  # Root path for /api/users/
    path("predict-relapse/", get_relapse_prediction, name="predict_relapse"),
    path("delete/", delete_account, name="delete_account"),
    path("disable/", disable_account, name="disable_account"),
    path("enable/", enable_account, name="enable_account"),
    path("login/", login_or_register, name="login"),
    path("login/google/", login_with_google, name="login_google"),
    path("logoutt/", logout, name="logout"),
    path("password/reset/", reset_password, name="reset_password"),
    path("profile/", get_user_profile, name="profile"),
    path("updateprofile/", update_user_profile, name="updateprofile"),
    path("signup/google/", signup_with_google, name="signup_google"),
    path("signup/", signup, name="signup"),
    path('update/', update_account, name='update_account'),
    
]
