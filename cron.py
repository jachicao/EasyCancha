from crontab import CronTab

cron = CronTab(user='root')
job = cron.new(command='python3 /root/easycancha/main.py')

job.hour.every(1)

cron.write()

job.enable()
