# -*- coding: utf-8 -*-
from common.models.pay.PayOrder import  PayOrder
from common.libs.Helper import getFormatDate
from common.libs.pay.PayService import PayService
import datetime
from application import app,db
'''
python manager.py runjob -m pay/index
'''

class JobTask():
	def __init__(self):
		pass
	def run(self,params):
		now = datetime.datetime.now()
		date_before_30min = now + datetime.timedelta( minutes = -30 )
		list = PayOrder.query.filter_by( status = -8 ).\
			filter( PayOrder.created_time <= getFormatDate( date = date_before_30min ) ).all()
		if not list:
			app.logger.info("no data~~")
			return

		pay_target = PayService()
		for item in list:
			pay_target.closeOrder( pay_order_id = item.id )
		app.logger.info("it's over~~")