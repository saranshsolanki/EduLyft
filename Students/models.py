from django.db import models


# Create your models here.

class StudentAnswers(models.Model):
    student = models.ForeignKey('auth.User')
    question = models.ForeignKey('tests.Questions')
    attempt_ans = models.CharField(max_length=100, blank = True)
    score = models.IntegerField(max_length = 5)
    is_answered = models.BooleanField()
    is_correct = models.NullBooleanField()
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.attempt_ans

