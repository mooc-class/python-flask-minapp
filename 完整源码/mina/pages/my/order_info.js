var app = getApp();
Page({
    data: {},
    onLoad: function (e) {
        var that = this;
        that.setData({
            order_sn: e.order_sn
        });
    },
    onShow: function () {
        this.getPayOrderInfo();
    },
    getPayOrderInfo:function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/my/order/info"),
            header: app.getRequestHeader(),
            data: {
                order_sn:that.data.order_sn
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                   info:resp.data.info
                });
            }
        });
    }
});