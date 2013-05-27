from django.db import models
from django.contrib import admin

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

#class PersonAdmin(admin.ModelAdmin): 
#    list_display = ('first_name', 'last_name')

#admin.site.register(Person, PersonAdmin)
admin.site.register(Person)

class BannedPerson(models.Model):
    name = models.OneToOneField(Person, related_name='is banned')
    timestamp = models.DateTimeField()
    def __unicode__(self):
        return self.name.first_name+' '+self.name.last_name

class BannedPersonAdmin(admin.ModelAdmin): 
    list_display = ('name', 'timestamp')

admin.site.register(BannedPerson, BannedPersonAdmin)

class Log(models.Model):
    name = models.ForeignKey(Person, related_name='logs')
    timestamp = models.DateTimeField()
    def __unicode__(self):
        return self.name.first_name+' '+self.name.last_name

class LogAdmin(admin.ModelAdmin): 
    list_display = ('name', 'timestamp')

admin.site.register(Log, LogAdmin)