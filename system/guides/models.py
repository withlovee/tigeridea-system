from django.db import models
from django.contrib import admin
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.defaultfilters import slugify
from django.db.models import Max

class Person(models.Model):
	no = models.IntegerField(primary_key=True)
	name_prefix = models.CharField(max_length=100, blank=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	organization = models.CharField(max_length=100, blank=True)

	def filename(self, filename):
		if self.no:
			num = self.no
		else:
			max_number = Person.objects.all().aggregate(Max('no'))
			if max_number['no__max']:
				num = max_number['no__max']+1
			else:
				num = 1
		fname, dot, extension = filename.rpartition('.')
		return 'people/'+'%s.%s' % (num, extension)

	image = models.FileField(upload_to=filename, blank=True)

	def save(self, *args, **kwargs):
		# delete old file when replacing by updating the file
		try:
			curr_img = Person.objects.get(no=self.no)
			if curr_img.image != self.image:
				curr_img.image.delete(save=False)
		except: pass # when new photo then we do nothing, normal case          
		super(Person, self).save(*args, **kwargs)

	def __unicode__(self):
		return u'%s %s %s %s' % (self.no, self.name_prefix, self.first_name, self.last_name)
		
	@models.permalink
	def get_absolute_url(self):
		return ('view_person', (), {'no': self.no})

class PersonAdmin(admin.ModelAdmin): 
	#change_list_template = 'smuggler/change_list.html'
	fieldsets = [('Name', {'fields': ('first_name', 'last_name')}),]
	list_display = ('first_name', 'last_name')
	search_fields = ['first_name', 'last_name']
	#list_filter = ('first_name', 'last_name')

#admin.site.register(Person, PersonAdmin)
admin.site.register(Person)

class BannedPerson(models.Model):
	name = models.OneToOneField(Person, related_name='is banned')
	timestamp = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.name.name_prefix+self.name.first_name+' '+self.name.last_name

class BannedPersonAdmin(admin.ModelAdmin): 
	list_display = ('name', 'timestamp')
	list_filter = ['timestamp']
	search_fields = ['name__first_name', 'name__last_name']

admin.site.register(BannedPerson, BannedPersonAdmin)

class Log(models.Model):
	name = models.ForeignKey(Person, related_name='logs')
	timestamp = models.DateTimeField()
	def __unicode__(self):
		return self.name.name_prefix+self.name.first_name+' '+self.name.last_name

class LogAdmin(admin.ModelAdmin): 
	list_display = ('name', 'timestamp')
	list_filter = ['timestamp']
	search_fields = ['name__first_name', 'name__last_name']

admin.site.register(Log, LogAdmin)
