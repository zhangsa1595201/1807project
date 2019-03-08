from django.core.cache import cache
from django.core.mail import send_mail
import uuid
import hashlib

# 生成唯一标示
def get_token():
    uuid_str = str(uuid.uuid4()).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

# 发送邮件
def send_verify_mail(email):
    token = get_token()
    cache.set(token, email, 60*60*3)
    from_email = "2269579003@qq.com"
    recs = [email]
    title = "爱鲜蜂激活邮件"
    confirm_url = "http://47.111.23.217:12348/axf/active/" + token
    message = "请点击以下链接进行激活" + confirm_url
    send_mail(title, message, from_email, recs)
