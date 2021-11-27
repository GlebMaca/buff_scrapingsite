import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
class Question(models.Model):
    question_text=models.CharField(max_length=200)
    pub_state=models.DateTimeField('date published')
    # @admin.display(
    #     boolean=True,
    #     ordering='pub_state',
    #     description='Published recently?',
    # )
    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        # return self.pub_state>=timezone.now()-datetime.timedelta(days=1)
        now=timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_state<=now
    
class Choice(models.Model):
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    choice_text=models.CharField(max_length=200)
    votes=models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text


# Create your models here.
