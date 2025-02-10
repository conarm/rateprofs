from django.db import models

# Tutorial models
# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField("date published")


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
    
# My own models
# TODO: check f2f relation parameters make sense
# TODO: check if year is stored correctly
# TODO: check if we need to limit integer - especially year and semester
# TODO: check whether to use "professors" or "teachers" on a module instance

class User(models.Model):
    username = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    password = models.CharField(max_length=250)
    
class Module(models.Model):
    name = models.CharField(max_length=250)
    
class Professor(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    
class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField()
    professors = models.ManyToManyField(Professor, related_name='modules')