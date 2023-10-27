
# lcoal database

# 关闭Debug, 使用nginx部署静态文件
# DEBUG = False
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'webarar',
#         'HOST': '127.0.0.1',
#         'PORT': 3306,
#         'USER': 'root',
#         'PASSWORD': 'password'
#     }
# }


# SECURITY安全设置 - 支持http时建议开启
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True # 将所有非SSL请求永久重定向到SSL
# SESSION_COOKIE_SECURE = True # 仅通过https传输cookie
# CSRF_COOKIE_SECURE = True # 仅通过https传输cookie
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True # 严格要求使用https协议传输
# SECURE_HSTS_PRELOAD = True # HSTS为
# SECURE_HSTS_SECONDS = 60
# SECURE_CONTENT_TYPE_NOSNIFF = True # 防止浏览器猜测资产的内容类型
