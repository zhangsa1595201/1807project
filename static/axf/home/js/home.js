$(function () {
    init_top_swiper();
    init_must_buy();
});
// 轮播图
function init_top_swiper() {
    var mySwiper = new Swiper('#topSwiper', {
        loop: true, // 循环模式选项
        // 如果需要分页器
        pagination: {
            el: '.swiper-pagination',
        },
        autoplay: 2000,
        // 如果需要前进后退按钮
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    })
}
// 必购
function init_must_buy() {
    var swiper = new Swiper('#swiperMenu', {
        loop: true, // 循环模式选项
        autoplay: 2000,
        slidesPerView: 3,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });
}