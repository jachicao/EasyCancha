from django.db import models
from django.db.models.signals import pre_save
from django.utils.timezone import localtime
from .cipher import AESCipher

LENGTH_16 = 16
LENGTH_32 = 32
LENGTH_64 = 64
LENGTH_128 = 128
LENGTH_256 = 256

# Create your models here.


class Platform(models.Model):
    NAME_EASYCANCHA = 'easycancha'
    SEED_LIST = [
        NAME_EASYCANCHA
    ]
    name = models.CharField(unique=True, max_length=LENGTH_32)

    def __str__(self):
        return f'{self.name}'


class PlatformUser(models.Model):
    username = models.CharField(unique=True, max_length=LENGTH_32)
    password = models.CharField(max_length=LENGTH_256)

    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.username} - {self.platform}'


def encrypt(string):
    aes = AESCipher()
    return aes.encrypt(string).decode()


def platformuser_pre_save(sender, instance, *args, **kwargs):
    instance.password = encrypt(instance.password)


pre_save.connect(platformuser_pre_save, sender=PlatformUser)


class Weekday(models.Model):
    NAME_DICT = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }

    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=LENGTH_32)

    def __str__(self):
        return f'{self.name}'


class Sport(models.Model):
    NAME_TENNIS = 'Tenis'
    SEED_LIST = [
        NAME_TENNIS
    ]
    name = models.CharField(unique=True, max_length=LENGTH_128)

    def __str__(self):
        return f'{self.name}'


class Club(models.Model):
    name = models.CharField(unique=True, max_length=LENGTH_128)
    easycancha_id = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.name}'


class ClubSport(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.club} - {self.sport}'

    class Meta:
        unique_together = ('club', 'sport')


class RecurrentReservation(models.Model):
    clubsport = models.ForeignKey(ClubSport, on_delete=models.CASCADE)
    weekday = models.ForeignKey(Weekday, on_delete=models.CASCADE)

    platformuser = models.ForeignKey(PlatformUser, on_delete=models.CASCADE)

    hour = models.IntegerField()
    minute = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return f'{self.clubsport} - {self.weekday} - ' \
            f'{str(self.hour).zfill(2)}:{str(self.minute).zfill(2)} - '\
            f'{self.duration} minutes'


class OneTimeReservation(models.Model):
    clubsport = models.ForeignKey(ClubSport, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    duration = models.IntegerField()

    platformuser = models.ForeignKey(PlatformUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.clubsport} - {localtime(self.datetime)} '\
            f'- {self.duration} minutes'
