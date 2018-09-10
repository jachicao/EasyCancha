from crontab import CronTab

cron = CronTab(tabfile='/etc/crontab')
job = cron.new(command='python main.py')

job.hour.every(1)

cron.write()
