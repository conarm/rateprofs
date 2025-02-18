from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
    
# TODO: check f2f relation parameters make sense
# TODO: check if year is stored correctly
# TODO: check if we need to limit integer - especially year and semester
# TODO: check whether to use "professors" or "teachers" on a module instance
    
class Module(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    
class Professor(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    
class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField()
    professors = models.ManyToManyField(Professor, through='ModuleInstanceProfessor')
    
class ModuleInstanceProfessor(models.Model):
    moduleInstance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    # @property
    # def average_rating(self):
    #     return self.rating_set.all().aggregate(Avg('rate'))['rate__avg']
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moduleInstanceProfessor = models.ForeignKey(ModuleInstanceProfessor, on_delete=models.CASCADE)
    rating = models.IntegerField()
    