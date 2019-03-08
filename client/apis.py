from django.contrib.auth import login
from django.http import JsonResponse, QueryDict
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *
from .auth import MyBackend
from .verify_send import *
from .authentications import *
from .util import get_sum_money

class LoginAPI(View):
    def post(self, req):
        u_name = req.POST.get("uname")
        pwd = req.POST.get("pwd")
        if u_name and len(u_name) >= 3:
            user = MyBackend.authenticate(self, req,username=u_name, password=pwd)
            if user:
                login(req, user)
                data = {
                    "code": 0,
                    "msg": "登陆成功",
                    "data": reverse("axf:mine")
                }
                return JsonResponse(data)
            else:
                data = {
                    "code": 1,
                    "msg": "用户名或密码错误"
                }
                return JsonResponse(data)
        else:
            data = {
                "code": 1,
                "msg": "用户名过短"
            }
            return JsonResponse(data)

class RegisterAPI(View):
    def post(self, req):
        username = req.POST.get("username")
        pwd = req.POST.get("pwd")
        confirm_pwd = req.POST.get("confirm_pwd")
        email = req.POST.get("email")
        icon = req.FILES.get("icon")
        # if username and len(username) >= 3 and pwd and pwd == confirm_pwd:
        #     if MyUser.objects.filter(username=username).exists():
        #         data = {
        #             "code": 1,
        #             "msg": "账户已注册"
        #         }
        #         return JsonResponse(data)
        #     else:
        #         user = MyUser.objects.create_user(
        #             username=username,
        #             email=email,
        #             is_active=False,
        #             password=pwd,
        #             icon=icon
        #         )
        #         send_verify_mail(email)
        #         data = {
        #             "code": 0,
        #             "data": reverse("axf:login")
        #         }
        #         return JsonResponse(data)
        # else:
        #     data = {
        #         "code": 1,
        #         "msg": "用户名过短或密码不一样"
        #     }
        #     return JsonResponse(data)
        if MyUser.objects.filter(username=username).exists():
            data = {
                "code": 1,
                "msg": "账户已注册"
            }
            return JsonResponse(data)
        else:
            if username and len(username) >= 3 and pwd and pwd == confirm_pwd:
                user = MyUser.objects.create_user(
                    username=username,
                    email=email,
                    is_active=False,
                    password=pwd,
                    icon=icon
                )
                send_verify_mail(email)
                data = {
                    "code": 0,
                    "data": reverse("axf:login")
                }
                return JsonResponse(data)
            else:
                data = {
                    "code": 2,
                    "msg": "用户名过短或密码不一样或其余信息未输入"
                }
                return JsonResponse(data)

class ItemCartAPI(CreateAPIView, UpdateAPIView):
    queryset = Cart.objects.all()
    authentication_classes = [LoginAuthentication]
    serializer_class = CartSerializer
    def post(self,request,*args,**kwargs):
        user = request.user
        if not user:
            res = {
                "msg":"not login",
                "code":1,
                "data":reverse("axf:login")
            }
            return Response(res)

        request.data._mutable = True
        request.data["user"] = user.id
        request.data._mutable = False
        goods_id = request.data.get("goods")
        goods = Goods.objects.get(pk=goods_id)
        num = int(request.data.get("num"))
        if num > goods.storenums:
            res = {
                "code":2,
                "msg":"商品库存不足",
                "data":None
            }
            return Response(res)

        cart_items = Cart.objects.filter(
            user=user,
            goods_id=goods_id
        )
        if cart_items.exists():
            cart_items = cart_items.first()
            cart_items.num += int(num)
            cart_items.save()
            res = {
                "code":0,
                "msg":"ok",
                "data":self.get_serializer(cart_items).data
            }
            return Response(res)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            res = {
                "code":0,
                "msg":"ok",
                "data":serializer.data
            }
            return Response(res,status=status.HTTP_201_CREATED, headers=headers)
            # return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        user = request.user
        if not user:
            res = {
                "msg": "not login",
                "code": 1,
                "data": reverse("axf:login")
            }
            return Response(res)
        request.data._mutable = True
        num = int(request.data.get("num"))
        if num < 1:
            res = {
                "code":1,
                "msg":"数量不合法",
                "data":""
            }
            return Response(res)
        cart_data = Cart.objects.get(user_id=user.id,goods_id=request.data.get("goods"))
        cart_num = 0
        cart_data.num -= num
        if cart_data.num == 0:
            cart_data.delete()
        else:
            cart_data.save()
            cart_num = cart_data.num
        res = {
            "code":0,
            "msg":"ok",
            "data":cart_num
        }
        return Response(res)

class CartItemStatusAPI(View):
    def put(self,request):
        params = QueryDict(request.body)
        user = request.user
        cart_id = params.get("cid")
        cart_item = Cart.objects.get(pk=cart_id)
        cart_item.is_select = not cart_item.is_select
        cart_item.save()
        is_select_all = True
        cart_items = Cart.objects.filter(user=user)
        if cart_items.filter(is_select=False).exists():
            is_select_all=False
        money = get_sum_money(cart_items)
        res = {
            "code":0,
            "msg":"ok",
            "data":{
                "current_item_status":cart_item.is_select,
                "is_select_all":is_select_all,
                "money":"%.2f"%money,
            }
        }
        return JsonResponse(res)

def cart_data_status_api(request):
    user = request.user
    if not user.is_authenticated:
        raise Exception("你未登录")
    carts = Cart.objects.filter(user_id=user.id)
    if not carts.exists():
        raise Exception("你的购物车暂无商品")
    is_select_all = carts.filter(is_select=False).exists()
    carts.update(is_select=is_select_all)
    sum_money = get_sum_money(carts) if is_select_all else 0
    res = {
        "code":0,
        "msg":"ok",
        "data":{
            "is_select_all":is_select_all,
            "sum_money":sum_money,
        }
    }
    return JsonResponse(res)

class CartDataOptionAPI(View):
    def put(self,req):
        params = QueryDict(req.body)
        user = req.user
        if not user.is_authenticated:
            raise Exception("请先登录")
        cart_data = Cart.objects.get(pk=params.get("cid"))
        option = params.get("option")
        if option == "add":
            cart_data.num += 1
            cart_data.save()
        else:
            cart_data.num -= 1
            if cart_data.num == 0:
                cart_data.delete()
            else:
                cart_data.save()
        cart_items = Cart.objects.filter(user=user)
        sum_money = get_sum_money(cart_items)
        is_select_all = (not cart_items.filter(is_select=False).exists()) and cart_items.exists()
        res = {
            "code":0,
            "msg":"ok",
            "data":{
                "sum_money":sum_money,
                "current_num":cart_data.num,
                "is_select_all":is_select_all,
            }
        }
        return JsonResponse(res)

class OrderItemAPT(DestroyAPIView):
    queryset = OrderItem.objects.filter(order__status=1)
    authentication_classes = [LoginAuthentication]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        order_id = request.data.get("order_id")
        order_items = self.queryset.filter(order__number=order_id)
        sum_money = 0
        for i in order_items:
            sum_money += (i.goods_num * i.price)
        res = {
            "code":0,
            "msg":"ok",
            "data":{
                "sum_money":sum_money,
            }
        }
        return Response(res)
