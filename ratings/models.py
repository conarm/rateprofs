from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
    
class Module(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250, unique=True)
    
class Professor(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250, unique=True)
    
class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField(validators=[
        MaxValueValidator(2),
        MinValueValidator(1)
    ])
    professors = models.ManyToManyField(Professor, through='ModuleInstanceProfessor')
    
class ModuleInstanceProfessor(models.Model):
    moduleInstance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moduleInstanceProfessor = models.ForeignKey(ModuleInstanceProfessor, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])
    