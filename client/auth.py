from django.contrib.auth.backends import ModelBackend
from .models import MyUser

class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            raise Exception("用户名或密码要求必填")
        user = None
        try:
            # 先按照用户名去搜索
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            try:
                # 按照邮箱搜索
                user = MyUser.objects.get(email=username)
            except MyUser.DoesNotExist:
                return None
        # 校验密码以及是否激活
        if user and user.check_password(password) and user.is_active:
            return user
        else:
            return None