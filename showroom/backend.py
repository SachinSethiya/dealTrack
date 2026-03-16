from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class ShowroomBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        try:
            # Adjust field if your Showroom model uses 'email' or 'username'
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None