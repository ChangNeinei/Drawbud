from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='profile')
    bio_text = models.TextField(max_length=500)
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + ' , ' + self.bio_text + '.' + str(self.score)


class Room(models.Model):
    owner = models.OneToOneField(User, on_delete=models.PROTECT, default=None)
    room_name = models.TextField(max_length=500)
    max_player_number = models.IntegerField()
    curr_player_number = models.IntegerField(default=0)
    description = models.TextField(max_length=500, blank=True)
    start_game = models.BooleanField(default=False)
    word = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.room_name + ', max player number ' +  str(self.max_player_number)

class Player(models.Model):
    username = models.CharField(max_length=20, default=None)
    room_name = models.TextField(max_length=500)

    def __str__(self):
        return self.room_name + ', user name' +  str(self.username)

class Drawing(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.TextField(max_length=500)
	image = models.FileField(blank=True)
	content_type = models.CharField(max_length=50)
