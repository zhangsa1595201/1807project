$(function () {
    $("#confirm_pwd").blur(function () {
        $("#error_ver_msg").text("");
        var pwd = $("#pwd").val();
        var confirm_pwd = $("#confirm_pwd").val();
        if (pwd != confirm_pwd) {
            $("#error_ver_msg").text("密码和确认密码不一致");
        }
    });

    $("#uname").blur(function () {
        $("#error_msg").text("");
        var name = $("#uname").val();
        if (name.length < 3) {
            $("#error_msg").text("用户名过短");
        }
        var actualdata = new FormData();
        actualdata.append("username", name);
        $.ajax({
            url: "/api/client/v1/register",
            data: actualdata,
            processData: false,
            cache: false,
            contentType: false,
            method: "post",
            success: function (res) {
                console.log(res);
                if (res.code == 1) {
                    $("#error_msg").text(res.msg);
                }
            }
        })
    });
    $("button").click(function () {
        var email = $("#email").val();
        var file = $("#icon")[0].files[0];

        var enc_pwd = md5(pwd);
        var enc_confirm_pwd = md5(confirm_pwd);

        if (file.size == 0) {
            alert("请选择头像");
            return;
        }
        var formdata = new FormData();
        formdata.append("username", name);
        formdata.append("pwd", enc_pwd);
        formdata.append("confirm_pwd", enc_confirm_pwd);
        formdata.append("email", email);
        formdata.append("icon", file);
        $.ajax({
            url: "/api/client/v1/register",
            data: formdata,
            processData: false,
            cache: false,
            contentType: false,
            method: "post",
            success: function (res) {
                console.log(res);
                if (res.code == 0) {
                    window.open(res.data, target = "_self");
                } else {
                    alert(res.msg);
                }
            }
        })
    });
})