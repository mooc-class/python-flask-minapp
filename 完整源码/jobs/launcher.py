# -*- coding: utf-8 -*-
from application import app,manager
from flask_script import Command,Option
import argparse,sys,traceback

'''
python manage.py runjob -m Test  (  jobs/tasks/Test.py )
python manage.py runjob -m test/Index (  jobs/tasks/test/Index.py )
* name or flags - 名称或选项字符串列表, e.g. foo or -f, --foo.
* action - 参数如果定义了选项，表示这是一个操作参数，至于调用时做哪种操作由用户输入或者default决定。
* nargs - 应该使用的命令行参数数。.
* const - 某些动作或参数个数的常数值。.
* default - 如果命令行没有对输入这个参数相应的值，则此参数用default给出的值.
* type -将用户输入的值转化为哪种类型.
* choices - 参数可输入值的范围或选择.
* required - 命令行输入的值是否可以被忽略（布尔量）.
* help - 参数的简要描述.
* metavar - useage中显示的参数的名称.
* dest - 要添加到解析参数返回的对象中的属性的名称.
'''
class runJob( Command ):

    capture_all_args = True
    def run(self,*args,**kwargs):
        args = sys.argv[2:]
        parser = argparse.ArgumentParser( add_help = True )

        parser.add_argument("-m","--name",dest = "name",metavar = "name", help="指定job名",required=True)
        parser.add_argument("-a","--act",dest = "act",metavar = "act", help="Job动作",required=False)
        parser.add_argument("-p","--param",dest = "param",nargs = "*", metavar = "param",help="业务参数",default = '',required=False)
        params = parser.parse_args( args )
        params_dict = params.__dict__
        ret_params = {}
        for item in params_dict.keys():
            ret_params[ item ] = params_dict[ item ]

        if "name" not in ret_params or not ret_params['name']:
            return self.tips()

        module_name = ret_params['name'].replace( "/","." )
        try:
            import_string = "from jobs.tasks.%s import JobTask as  job_target" % ( module_name )
            exec( import_string , globals() )
            target = job_target()
            target.run( ret_params )
        except Exception as e:
            traceback.print_exc()


    def tips(self):
        tip_msg = '''
            请正确调度Job
            python manage runjob -m Test  (  jobs/tasks/Test.py )
            python manage runjob -m test/Index (  jobs/tasks/test/Index.py )
        '''
        app.logger.info( tip_msg )
        return False
