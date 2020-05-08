# -*- coding:utf-8 -*-

import os
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

# @sched.scheduled_job('cron', hour=0, minute=0)
# def scheduled_job():
#     print ("daily vote")
#     os.system("bash scripts/_execute.sh")

sched.start()
