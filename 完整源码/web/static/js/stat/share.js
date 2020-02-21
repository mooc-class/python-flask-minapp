;
var stat_share_ops = {
    init:function(){
        this.eventBind();
        this.drawChart();
        this.datetimepickerComponent();
    },
    eventBind:function(){
        $("#search_form_wrap .search").click( function(){
            $("#search_form_wrap").submit();
        });
    },
    datetimepickerComponent:function(){
        var that = this;
        $.datetimepicker.setLocale('zh');
        params = {
            scrollInput: false,
            scrollMonth: false,
            scrollTime: false,
            dayOfWeekStart: 1,
            lang: 'zh',
            todayButton: true,//回到今天
            defaultSelect: true,
            defaultDate: new Date().Format('yyyy-MM-dd'),
            format: 'Y-m-d',//格式化显示
            timepicker: false
        };
        $('#search_form_wrap input[name=date_from]').datetimepicker(params);
        $('#search_form_wrap input[name=date_to]').datetimepicker(params);

    },
    drawChart:function(){
        charts_ops.setOption();
        $.ajax({
            url:common_ops.buildUrl("/chart/share"),
            dataType:'json',
            success:function( res ){
                charts_ops.drawLine( $('#container'),res.data )
            }
        });
    }
};

$(document).ready( function(){
    stat_share_ops.init();
});
