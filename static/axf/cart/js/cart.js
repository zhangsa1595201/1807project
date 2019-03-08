$(function () {
    $(".subCart").click(function () {
        var $btn = $(this);
        var cid = $btn.parents("li").attr("cart_id");
        $.ajax({
            url:"/api/client/v1/cart/options",
            data:{
                cid:cid,
                option:"sub",
            },
            method:"put",
            success:function (res) {
                if (res.code == 0){
                   if(res.data.current_num != 0){
                       $btn.next().text(res.data.current_num);
                   }else{
                       $btn.parents("li").remove();
                   }
                   $("#sum_money").text(res.data.sum_money);
                }else {
                    alert(res.msg)
                }
                var text = res.data.is_select_all?"√":"";
                $(".all_select>span>span").text(text);

            }
        });
    });

    $(".addCart").click(function () {
        var $btn = $(this);
        var cid = $btn.parents("li").attr("cart_id");
        $.ajax({
            url:"/api/client/v1/cart/options",
            data:{
                cid:cid,
                option:"add",
            },
            method:"put",
            success:function (res) {
                if (res.code == 0){
                   $btn.prev().text(res.data.current_num);
                   $("#sum_money").text(res.data.sum_money);
                }else {
                    alert(res.msg)
                }
            }
        });
    });

    $(".all_select").click(function () {
        $.ajax({
            url:"/api/client/v1/cart-status",
            success:function (res) {
                if (res.code == 0){
                    var text = res.data.is_select_all?"√":"";
                    $(".all_select>span>span").text(text);
                    $("#sum_money").text(res.data.sum_money);
                    $(".confirm").each(function () {
                        $(this).find("span").find("span").text(text)
                    })
                }
            }
        });
    });

    $(".confirm").click(function () {
        var $current_btn = $(this);
        var cid = $current_btn.parents("li").attr("cart_id");
        $.ajax({
            url:"/api/client/v1/cart/status",
            data:{
                cid:cid,
            },
            method:"put",
            success:function (res) {
                if (res.code == 0){
                    if (res.data.is_select_all){
                        $(".all_select>span>span").html("√")
                    }else{
                        $(".all_select>span>span").html("")
                    }
                    $("#sum_money").html(res.data.money);
                    if (res.data.current_item_status){
                        $current_btn.find("span").find("span").html("√");
                    }else{
                        $current_btn.find("span").find("span").html("");
                    }
                }else{
                    alert(res.msg)
                }
            }
        })
    })
})