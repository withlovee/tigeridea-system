from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from guides.forms import AddPersonForm
from guides.models import Person, BannedPerson
from xlwt import *
import zipfile
from datetime import datetime
import os.path

def list_person(request):
	people = Person.objects.all()
	page = request.GET.get('p')
	entries_per_page = 2
	
	queries_without_page = request.GET.copy()
	if queries_without_page.has_key('p'):
		del queries_without_page['p']

	# Get Search Query
	no1 = request.GET.get('no1')
	no2 = request.GET.get('no2')
	first_name = request.GET.get('first_name')
	last_name = request.GET.get('last_name')

	# Filter Search
	if no1 :
		people = people.filter(no__gte=no1)
	if no2 :
		people = people.filter(no__lte=no2)
	if first_name :
		people = people.filter(first_name__contains=first_name)
	if last_name :
		people = people.filter(last_name__contains=last_name)

	# Pagination
	paginator = Paginator(people, entries_per_page)
	try:
		people = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		people = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		people = paginator.page(paginator.num_pages)

	return render(request, 
		'list.html', 
		{
		'people': people, 
		'queries': queries_without_page, 
		'queries_list': request.GET.dict(),
		}
	)
def list_banned(request):
	people = BannedPerson.objects.all()
	page = request.GET.get('p')
	entries_per_page = 2
	
	queries_without_page = request.GET.copy()
	if queries_without_page.has_key('p'):
		del queries_without_page['p']

	# Get Search Query
	no1 = request.GET.get('no1')
	no2 = request.GET.get('no2')
	first_name = request.GET.get('first_name')
	last_name = request.GET.get('last_name')

	# Filter Search
	if no1 :
		people = people.filter(name__no__gte=no1)
	if no2 :
		people = people.filter(name__no__lte=no2)
	if first_name :
		people = people.filter(name__first_name__contains=first_name)
	if last_name :
		people = people.filter(name__last_name__contains=last_name)

	# Pagination
	paginator = Paginator(people, entries_per_page)
	try:
		people = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		people = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		people = paginator.page(paginator.num_pages)

	return render(request, 
		'list_banned.html', 
		{
		'people': people, 
		'queries': queries_without_page, 
		'queries_list': request.GET.dict(),
		}
	)

def add_person(request):
	'''
	max_arr = Person.objects.all().aggregate(Max('no'))
	print max_arr
	if max_arr :
		max_no = max_arr['no__max']
	else :
		max_no = 0
	form = AddPersonForm(initial={'no': max_no+1})
	'''
	max_no = 0
	form = AddPersonForm()
	if request.method == 'POST':
		form = AddPersonForm(request.POST, request.FILES)
		if form.is_valid():
			person = form.save()
			person.user = request.user
			person.save()
			# Success
			return redirect('/view/'+str(person.no))
	return render(request, 'add_person.html', {'form': form, 'max_number': max_no})

def view_person(request, no):
	person_no = no
	person = Person.objects.get(no=person_no)
	try: 
		BannedPerson.objects.get(name__no=person_no)
		banned = True
	except ObjectDoesNotExist:
		banned = False
	return render(request, 'view_person.html', {'person': person, 'banned': banned})

def export_banned(request):
	w = Workbook()
	ws = w.add_sheet('Banned List')
	people = BannedPerson.objects.all().order_by('name__no')
	text = XFStyle()
	time = XFStyle()
	time.num_format_str = 'M/D/YY h:mm'
	i = 0
	for person in people:
		ws.write(i, 0, person.name.no, text)
		ws.write(i, 1, person.name.first_name+" "+person.name.last_name, text)
		#ws.write(i, 2, person.timestamp, time)
		i += 1
	file_path = r""+os.path.dirname(__file__)+r"\uploads\export\banned_list.xls"
	w.save(file_path)
	return render(request, 'export_banned.html')

def export_person(request):
	people = Person.objects.all().order_by('no')
	files = []

	# Get Search Query
	no1 = request.GET.get('no1')
	no2 = request.GET.get('no2')
	# Filter Search
	if no1 :
		people = people.filter(no__gte=no1)
	if no2 :
		people = people.filter(no__lte=no2)

	w = Workbook()
	ws = w.add_sheet('People')
	text = XFStyle()
	time = XFStyle()
	time.num_format_str = 'M/D/YY h:mm'

	if no1 or no2:
		# Create data XLS
		i = 0
		for person in people:
			ws.write(i, 0, person.no, text)
			ws.write(i, 1, person.first_name+" "+person.last_name, text)
			ws.write(i, 2, person.organization, text)
			#ws.write(i, 2, person.timestamp, time)
			i += 1
		file_path = r""+os.path.dirname(__file__)+r"\uploads\export\export_list.xls"
		w.save(file_path)

		# Create Images Zip
		file_path = r""+os.path.dirname(__file__)+r"\uploads\export\export_images.zip"
		zf = zipfile.ZipFile(file_path, mode='w')
		try:
			for person in people:
				files.append(person.image.name);
				print 'adding '+person.image.path
				zf.write(person.image.path,person.image.name)
		finally:
			print 'closing'
			zf.close()

	return render(request, 'export_people.html', {'queries': request.GET.copy(), 'files': files})

class EditPerson(UpdateView):
	form_class = AddPersonForm
	model = Person
	template_name = 'edit_person.html'

class DeletePerson(DeleteView):
	model = Person
	template_name = 'delete_person.html'
	success_url = '/list/'

class AddBannedPerson(CreateView):
	model = BannedPerson
	template_name = 'add_banned.html'
	success_url = '/blacklist/'

class UnbanPerson(DeleteView):
	model = BannedPerson
	slug_field = 'name__no'
	template_name = 'unban_person.html'
	success_url = '/blacklist/'