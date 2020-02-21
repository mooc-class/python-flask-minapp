Job 列表
======
* 队列Job

        * * * * * { . ~/.bash_jobs && cd /data/www/Order && python manager.py runjob -m queue/index ;} >> /data/www/logs/queue_list.`date +\%Y_\%m_\%d`.log 2>&1
        * * * * * { . ~/.bash_jobs && cd /data/www/Order && python manager.py runjob -m pay/index ;} >> /data/www/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        1 2 * * { . ~/.bash_jobs && cd /data/www/Order && python manager.py runjob -m stat/daily -a member ;} >> /data/www/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        2 2 * * * { . ~/.bash_jobs && cd /data/www/Order && python manager.py runjob -m stat/daily -a food ;} >> /data/www/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        3 2 * * * { . ~/.bash_jobs && cd /data/www/Order && python manager.py runjob -m stat/daily -a site ;} >> /data/www/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1