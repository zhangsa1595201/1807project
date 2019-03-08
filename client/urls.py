from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r"^home$",home,name="home"),
    url(r"^cart$",cart,name="cart"),
    url(r"^market$",market,name="market"),
    url(r"^mine$",mine,name="mine"),
    url(r"^active/",active,name="active"),
    url(r"^register$",register_view,name="register"),
    url(r"^login$",login_view,name="login"),
    url(r"^logout$",logout_api,name="logout"),
    url(r"^market_with_params/(?P<type_id>\d+)/(?P<sub_type_id>\d+)/(?P<sort>\d+)$",market_with_params,name="market_with_params"),
    url(r"^order$",order_view,name="order"),
]