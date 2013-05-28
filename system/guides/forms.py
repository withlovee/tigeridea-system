#!-*- coding: utf-8 -*-
from django import forms
from django.utils.html import strip_tags
from guides.models import Person

class AddPersonForm(forms.ModelForm):
	class Meta:
		model = Person

	def __init__(self, *args, **kwargs):
		super(AddPersonForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs['placeholder'] = "First Name"
		self.fields['last_name'].widget.attrs['placeholder'] = "Last Name"
		self.fields['no'].widget.attrs['placeholder'] = "no"
		self.fields['first_name'].label = 'ชื่อจริง'
		self.fields['last_name'].label = 'นามสกุล'