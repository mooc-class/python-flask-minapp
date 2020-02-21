;
var finance_pay_info_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".express_send").click(function(){
            var data_id = $(this).attr("data");
            var callback = {
            'ok':function(){
                $.ajax({
                    url:common_ops.buildUrl( "/finance/ops" ),
                    type:'POST',
                    data:{
                        act:"express",
                        id:data_id
                    },
                    dataType:'json',
                    success:function( res ){
                        var callback = null;
                        if( res.code == 200 ){
                            callback = function(){
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert( res.msg,callback );
                    }
                });
            },
            'cancel':null
        };
        common_ops.confirm( "确定已发货了？", callback );
        });
    }
};

$(document).ready( function(){
    finance_pay_info_ops.init();
});

