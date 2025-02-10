from django.contrib import admin
from .models import User, Module, Professor, ModuleInstance

# Register your models here

admin.site.register(User)
admin.site.register(Module)
admin.site.register(Professor)
admin.site.register(ModuleInstance)