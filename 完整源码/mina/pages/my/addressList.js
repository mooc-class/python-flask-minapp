//获取应用实例
var app = getApp();
Page({
    data: {},
    onShow: function () {
        var that = this;
        this.getList();
    },
    //选中谁就把谁设置为默认的
    selectTap: function (e) {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/address/ops"),
            header: app.getRequestHeader(),
            method:'POST',
            data:{
                id:e.currentTarget.dataset.id,
                act:'default'
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                   list:resp.data.list
                });
            }
        });
        wx.navigateBack({});
    },
    addressSet: function (e) {
        wx.navigateTo({
            url: "/pages/my/addressSet?id=" + e.currentTarget.dataset.id
        })
    },
    getList:function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/my/address/index"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                   list:resp.data.list
                });
            }
        });
    }
});
