#!-*- coding: utf-8 -*-
from django import forms
from django.forms import Textarea
from django.utils.html import strip_tags
from guides.models import Person, Log

class AddPersonForm(forms.ModelForm):
	class Meta:
		model = Person
		widgets = {
			'note': Textarea(attrs={'cols': 120, 'rows': 5}),
		}
	def __init__(self, *args, **kwargs):
		super(AddPersonForm, self).__init__(*args, **kwargs)
		#self.fields['first_name'].widget.attrs['placeholder'] = "First Name"
		#self.fields['last_name'].widget.attrs['placeholder'] = "Last Name"
		#self.fields['no'].widget.attrs['placeholder'] = "no"
		self.fields['no'].label = 'เลขประจำตัว'
		self.fields['name_prefix'].label = 'คำนำหน้าชื่อ'
		self.fields['first_name'].label = 'ชื่อจริง'
		self.fields['last_name'].label = 'นามสกุล'
		self.fields['organization'].label = 'สังกัด'
		self.fields['image'].label = 'รูป'
		self.fields['note'].label = 'หมายเหตุ'

class LogForm(forms.ModelForm):
	class Meta:
		model = Log
	def __init__(self, *args, **kwargs):
		super(LogForm, self).__init__(*args, **kwargs)