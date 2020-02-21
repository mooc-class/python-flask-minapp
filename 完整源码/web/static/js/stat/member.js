;
var stat_member_ops = {
    init:function(){
        this.eventBind();
        this.datetimepickerComponent();
    },
    eventBind:function(){
        $("#search_form_wrap .search").click( function(){
            $("#search_form_wrap").submit();
        });
    },
    datetimepickerComponent:function() {
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
    }
};

$(document).ready( function(){
    stat_member_ops.init();
});
