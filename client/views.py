from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .util import get_sum_money, get_order_number
from .models import *
from .serializers import OrderItemSerializer
from django.conf import settings

# Create your views here.
def home(request):
    tops = Wheel.objects.all()
    navs = Nav.objects.all()
    mustbuys = MustBuy.objects.all()
    shops = Shop.objects.all()
    infos = MainShow.objects.all()
    data = {
        "title":"首页",
        "tops":tops,
        "navs":navs,
        "mustbuys":mustbuys,
        "shop_0":shops.first(),
        "shop_1_3":shops[1:3],
        "shop_4_7":shops[3:7],
        "shop_7_11":shops[7:11],
        "infos":infos
    }
    return render(request,"home/home.html",data)

def market_with_params(req,type_id,sub_type_id,sort):
    types = GoodsTypes.objects.all()
    goods_type = types.get(typeid=type_id)
    sub_types = goods_type.childtypenames.split("#")
    sub_type_datas = [i.split(":") for i in sub_types]
    # for i in sub_types:
    #     sub_type_datas.append(i.split(":"))
    goods = Goods.objects.filter(categoryid=type_id)
    if sub_type_id != "0":
        goods = goods.filter(childcid=sub_type_id)
    if sort == "1":
        goods = goods.order_by("price")
    elif sort == "2":
        goods = goods.order_by("-productnum")
    else:
        pass
    if req.user.is_authenticated:
        if hasattr(req.user,"cart_set"):
            cart_data = req.user.cart_set.all()
            for good in goods:
                cart_goods = cart_data.filter(goods=good)
                if cart_goods.exists():
                    good.cart_num = cart_goods.first().num
    data = {
        "title": "闪购",
        "types": types,
        "select_type_id":type_id,
        "goods":goods,
        "sub_types":sub_type_datas,
        "select_sub_type_id":sub_type_id,
        "current_sort":sort,
    }
    return render(req, "market/market.html", data)

def market(request):
    return redirect(reverse("axf:market_with_params",kwargs={"type_id":104749,"sub_type_id":0,"sort":0}))

@login_required(login_url="/axf/login")
def cart(request):
    user = request.user
    cartitems = Cart.objects.filter(user_id=user.id)
    is_select_all = True
    if cartitems.filter(is_select=False).exists():
        is_select_all = False
    money = get_sum_money(cartitems)
    data = {
        "title":"购物车",
        "cartitems":cartitems,
        "is_select_all":is_select_all,
        "money":"%.2f"%money,
    }
    return render(request,"cart/cart.html",data)

def mine(request):
    user = request.user
    # is_login = False
    # uname = ""
    # icon = ""
    # if user.is_authenticated:
    #     is_login = True
    #     uname = user.username
    #     icon = user.icon
    is_login, name, icon = (True, user.username, user.icon.url) if user.is_authenticated else (False, "", "")
    data = {
        "title":"我的",
        "is_login":is_login,
        "name":name,
        "icon":"http://{url}/static/uploads/{icon}".format(url=request.get_host(),icon=icon)
    }
    return render(request,"mine/mine.html",data)

def logout_api(req):
    logout(req)
    return redirect(reverse("axf:mine"))


# 生成唯一码，发送邮件，点击链接进行激活用户
def active(req):
    token = req.get_full_path()
    email = cache.get(token[12:])
    if email:
        user = MyUser.objects.filter(email=email)
        if user.count() == 1:
            user.update(is_active = True)
            return redirect(reverse('axf:login'))
        else:
            return HttpResponse("<h1>无邮箱或邮箱有多个</h1>")
    else:
        return HttpResponse("<h1>密码失效</h1>")

def register_view(req):
    return render(req,"user/register.html")

def login_view(req):
    return render(req,"user/login.html")

@login_required(login_url="/axf/login")
def order_view(request):
    user = request.user
    address = Address.objects.get(user_id=user.id,is_default=True)
    order = Order.objects.create(
        user_id=user.id,
        number= get_order_number(),
        adress=address,
    )
    cart_items = Cart.objects.select_related("goods").filter(
        user_id=user.id,
        is_select=True
    )
    if not cart_items.exists():
        raise Exception("你未选中任何商品")
    order_items = []
    for i in cart_items:
        desc = None
        if i.num > i.goods.storenums:
            desc = "当前库存不足，请稍后"
        order_item = OrderItem.objects.create(
            order_id=order.id,
            goods_num=i.num,
            goods_id=i.goods_id,
            price=i.goods.price,
            desc=desc
        )
        order_items.append(order_item)
    sum_money = get_sum_money(cart_items)
    cart_items.delete()
    data = {
        "sum_money":sum_money,
        "order_items":OrderItemSerializer(order_items,many=True).data,
        "order_number":order.number,
    }
    return render(request,"order/order.html",data)