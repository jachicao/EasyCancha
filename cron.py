from crontab import CronTab

cron = CronTab()
job = cron.new(command='python main.py')

job.hour.every(1)

cron.write()
