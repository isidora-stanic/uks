from django.contrib.auth.base_user import BaseUserManager

class GitUserManager(BaseUserManager):

    def create_user(self, username, password=None):

        if username is None:
            raise TypeError('Users must have a.')

        user = self.model(username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, password)
        user.is_superuser = True
        user.save()

        return user