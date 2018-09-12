from crontab import CronTab

cron = CronTab(user='root')
job = cron.new(command='python3 /root/easycancha/main.py')

job.hour.every(1)
job.every_reboot()
job.enable()

cron.write()
