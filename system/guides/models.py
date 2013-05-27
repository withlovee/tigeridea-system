from django.db import models

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Banned(models.Model):
    name = models.ForeignKey(Person, related_name='Name')
    date = models.DateTimeField()
    def __unicode__(self):
        return self.name