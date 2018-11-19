from django.contrib import admin

# Register your models here.
from .models import Club, ClubSport, RecurrentReservation, OneTimeReservation,\
    Platform, PlatformUser

#   admin.site.register(Weekday)
#   admin.site.register(Sport)
admin.site.register(Platform)
admin.site.register(PlatformUser)
admin.site.register(Club)
admin.site.register(ClubSport)
admin.site.register(RecurrentReservation)
admin.site.register(OneTimeReservation)
