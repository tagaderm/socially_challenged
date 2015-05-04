from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField(null=True)
    profile_pic = models.ImageField(upload_to='s_network/static/s_network/images', null=True, blank=True)
    email = models.EmailField()
    def __str__(self):
        return self.first_name+' '+self.last_name

class WallPost(models.Model):
    profile = models.ForeignKey(Profile, related_name='profile')
    poster = models.ForeignKey(Profile, related_name='poster', related_query_name='poster')
    post_text = models.CharField(max_length=1000)
    post_date_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.profile.first_name+' '+self.profile.last_name+':'+str(self.post_date_time)

class Comment(models.Model):
    wallpost = models.ForeignKey(WallPost)
    commenter = models.ForeignKey(Profile)
    comment_date_time = models.DateTimeField(auto_now=True)
    comment_text = models.CharField(max_length=1000)
    def __str__(self):
        return self.wallpost.profile.first_name+' '+self.wallpost.profile.last_name+':'+str(self.comment_date_time)

class Photo(models.Model):
    profile = models.ForeignKey(Profile)
    photo = models.ImageField(upload_to='s_network/static/s_network/images')
    def __str__(self):
        return self.photo.url
