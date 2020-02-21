;
//画图通用组件，虽然估计很难统一，但是总要走出第一步了
var charts_ops = {
    setOption:function(){
        Highcharts.setOptions({
            chart: {
            },
            exporting: {
                enabled: false
            },
            legend: {
                //enabled:false
            },
            credits:{
                enabled:false
            },
            colors:['#058DC7', '#50B432', '#ED561B', '#DDDF00',
                '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4','#E93EFF'],
            title: '',
            xAxis: {
                tickWidth:0,
                lineWidth: 0,
                gridLineColor: '#eee',
                //gridLineWidth: 1,
                crosshair: {
                    width: 1,
                    color: '#ebebeb'
                }
            },
            yAxis: {
                gridLineColor: '#eee',
                gridLineWidth: 1,
                title: ''
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    pointWidth: 20,
                    borderWidth: 0
                },
                series: {
                    marker: {
                        enabled: false
                    },
                },
                line: {
                    lineWidth: 2,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    }
                }
            },
            tooltip: {
                backgroundColor: '#404750',
                borderWidth: 0,
                shadow: false,
                headerFormat: '',
                footerFormat: '',
                shared: true,
                useHTML: true,
                style: {
                    color: '#fff',
                    padding: '5px'
                }
            },
            lang: {
                noData: "暂无数据"
            },
            noData: {
                style: {
                    fontWeight: 'bold',
                    fontSize: '15px',
                    color: '#303030'
                }
            }
        });
    },
    drawLine:function( target ,data ){//画直线
        var chart =  target.highcharts({
            chart: {
                type: 'spline'
            },
            xAxis: {
                categories: data.categories
            },
            series: data.series,
            legend: {
                enabled:true,
                align: 'right',
                verticalAlign: 'top',
                x: 0,
                y: -15
            }
        });
        return chart;
    }
};