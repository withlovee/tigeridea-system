#!-*- coding: utf-8 -*-
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Max, Count
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from guides.forms import AddPersonForm, LogForm
from guides.models import Person, BannedPerson, Log
from xlwt import *
import xlrd
import zipfile
from time import time
from datetime import datetime, date, timedelta
import os.path
import subprocess

def gitshell(request):
	# shell = subprocess.check_output(["/home/ubuntu/tigeridea-system/gitshell"])
	shell = subprocess.check_output(["service", "apache2", "reload"])
	return HttpResponse(shell)

def list_person(request):
	people = Person.objects.all()
	page = request.GET.get('p')
	entries_per_page = 30
	
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

def list_log(request):
	log = Log.objects.order_by('timestamp').reverse()
	page = request.GET.get('p')
	entries_per_page = 30
	
	queries_without_page = request.GET.copy()
	if queries_without_page.has_key('p'):
		del queries_without_page['p']

	# Get Search Query
	no1 = request.GET.get('no1')
	no2 = request.GET.get('no2')
	first_name = request.GET.get('first_name')
	last_name = request.GET.get('last_name')
	date = request.GET.get('date')
	month = request.GET.get('month')
	year = request.GET.get('year')

	# Filter Search
	if no1 :
		log = log.filter(name__no=no1)
	if first_name :
		log = log.filter(name__first_name__contains=first_name)
	if last_name :
		log = log.filter(name__last_name__contains=last_name)
	if year :
		log = log.filter(timestamp__year=int(year))
	if month :
		log = log.filter(timestamp__month=int(month))
	if date :
		log = log.filter(timestamp__day=int(date))

	# Pagination
	paginator = Paginator(log, entries_per_page)
	try:
		log = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		log = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		log = paginator.page(paginator.num_pages)

	for item in log:
		item.no = item.name.no
		item.first_name = item.name.first_name
		item.last_name = item.name.last_name
		item.organization = item.name.organization

	month_names = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 
					'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
	return render(request, 
		'list_log.html', 
		{
		'log': log, 
		'queries': queries_without_page, 
		'queries_list': request.GET.dict(),
		'date_list': range(1,32),
		'month_list': zip(month_names,range(1,13)),
		'year_list': range(2009,2021)
		}
	)

def list_banned(request):
	people = BannedPerson.objects.all()
	page = request.GET.get('p')
	entries_per_page = 30
	
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
	stat = []
	graph = []
	label = []
	person_no = no
	person = Person.objects.get(no=person_no)
	log = Log.objects.filter(name__no=person_no).order_by('timestamp')
	# Check is the person is banned
	try: 
		BannedPerson.objects.get(name__no=person_no)
		banned = True
	except ObjectDoesNotExist:
		banned = False
	# Get log stat
	stat_num = log.filter(name__no=person_no).aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	stat_num = log.filter(timestamp__gte = (date.today()-timedelta(days=6))).aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	stat_num = log.filter(timestamp__gte = (date.today()-timedelta(days=29))).aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	# For graph
	for i in range(0,30):
		day = date.today()-timedelta(days=i)
		stat_num = log.filter(timestamp__year=day.year,
			timestamp__month=day.month,
			timestamp__day=day.day
			).aggregate(Count('timestamp'))
		daystr = date.today()-timedelta(days=i+1)
		graph.append(stat_num['timestamp__count'])
	graph.reverse()
	stat_all = 'จำนวนครั้งที่เข้าทั้งหมด'
	stat_7 = 'จำนวนครั้งที่เข้าภายใน 7 วัน'
	stat_30 = 'จำนวนครั้งที่เข้าภายใน 30 วัน'
	begin_date = date.today()-timedelta(days=30)
	begin_date_arr = [begin_date.strftime('%d'),int(begin_date.strftime('%m'))-1,begin_date.strftime('%Y')]
	return render(request, 'view_person.html', {
		'person': person, 
		'begin_date': begin_date_arr,
		'stat': stat,
		'banned': banned,
		'graph': graph,
		'stat_all': stat_all,
		'stat_7': stat_7,
		'stat_30': stat_30,
		'enu_log': enumerate(log),
		})

def export_banned(request):
	w = Workbook()
	ws = w.add_sheet('Banned List')
	people = BannedPerson.objects.all().order_by('name__no')
	text = XFStyle()
	time = XFStyle()
	time.num_format_str = 'M/D/YY h:mm'
	# Create Header
	i = 0
	ws.write(i, 0, u"เลขประจำตัว", text)
	ws.write(i, 1, u"คำนำหน้า", text)
	ws.write(i, 2, u"ชื่อจริง", text)
	ws.write(i, 3, u"นามสกุล", text)
	ws.write(i, 4, u"สังกัด", text)
	ws.write(i, 5, u"ไฟล์รูป", text)
	ws.write(i, 6, u"หมายเหตุ", text)
	i += 1
	# Create data XLS
	for person in people:
		ws.write(i, 0, person.name.no, text)
		ws.write(i, 1, person.name.name_prefix, text)
		ws.write(i, 2, person.name.first_name, text)
		ws.write(i, 3, person.name.last_name, text)
		ws.write(i, 4, person.name.organization, text)
		ws.write(i, 5, person.image, text)
		ws.write(i, 6, person.note, text)
		#ws.write(i, 2, person.timestamp, time)
		i += 1
	file_path = r""+os.path.dirname(__file__)+r"/uploads/export/banned_list.xls"
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

	if no1 or no2:
		files = create_export_people(people)

	return render(request, 'export_people.html', {'queries': request.GET.copy(), 'files': files})

def export_person_all(request):
	people = Person.objects.all().order_by('no')
	files = create_export_people(people)

	return redirect("/uploads/export/export_list.xls")

def create_export_people(people):
	files = []

	w = Workbook()
	ws = w.add_sheet('People')
	text = XFStyle()
	time = XFStyle()
	time.num_format_str = 'M/D/YY h:mm'

	# Create Header
	i = 0
	ws.write(i, 0, u"เลขประจำตัว", text)
	ws.write(i, 1, u"คำนำหน้า", text)
	ws.write(i, 2, u"ชื่อจริง", text)
	ws.write(i, 3, u"นามสกุล", text)
	ws.write(i, 4, u"สังกัด", text)
	ws.write(i, 5, u"ไฟล์รูป", text)
	ws.write(i, 6, u"หมายเหตุ", text)
	i += 1
	# Create data XLS
	for person in people:
		ws.write(i, 0, person.no, text)
		ws.write(i, 1, person.name_prefix, text)
		ws.write(i, 2, person.first_name, text)
		ws.write(i, 3, person.last_name, text)
		ws.write(i, 4, person.organization, text)
		if person.image:
			ws.write(i, 5, person.image.url.replace('/uploads/',''), text)
		ws.write(i, 6, person.note, text)
		#ws.write(i, 2, person.timestamp, time)
		i += 1
	file_path = r""+os.path.dirname(__file__)+r"/uploads/export/export_list.xls"
	w.save(file_path)

	# Create Images Zip
	file_path = r""+os.path.dirname(__file__)+r"/uploads/export/export_images.zip"
	zf = zipfile.ZipFile(file_path, mode='w')
	try:
		for person in people:
			if person.image:
				files.append(person.image.name);
				print 'adding '+person.image.path
				zf.write(person.image.path,person.image.name)
	finally:
		print 'closing'
		zf.close()
	return files

def import_log(request):
	data = []
	if request.method == 'POST':
		log_file = request.FILES['file']
		path = default_storage.save('uploads/log.xls', ContentFile(log_file.read()))
		tmp_file = os.path.join(settings.MEDIA_ROOT, path)
		book = xlrd.open_workbook(tmp_file)
		sh = book.sheet_by_index(0)
		for i in range(sh.nrows):
			no = int(sh.cell_value(rowx=i, colx=0))
			time2 = int(sh.cell_value(rowx=i, colx=1))
			form = LogForm({'name': no, 'timestamp': datetime.fromtimestamp(time2)})
			if form.is_valid():
				try:
					log_result = form.save()
					data.append({
						'no': log_result.name.no,
						'name': log_result.name, 
						'timestamp': datetime.fromtimestamp(time2)
						})
				except IntegrityError:
					data.append({
						'no': no,
						'name': '-', 
						'timestamp': 'Duplicated Data'
						})
	return render(request, 'import_log.html', {'data': data})

def import_person(request):
	data = []
	if request.method == 'POST':
		log_file = request.FILES['file']
		path = default_storage.save('uploads/import_person.xls', ContentFile(log_file.read()))
		tmp_file = os.path.join(settings.MEDIA_ROOT, path)
		book = xlrd.open_workbook(tmp_file)
		sh = book.sheet_by_index(0)
		for i in range(1, sh.nrows+1):
			no = sh.cell_value(rowx=i, colx=0)
			name_prefix = sh.cell_value(rowx=i, colx=1)+u""
			first_name = sh.cell_value(rowx=i, colx=2)+u""
			last_name = sh.cell_value(rowx=i, colx=3)+u""
			organization = sh.cell_value(rowx=i, colx=4)+u""
			#image = sh.cell_value(rowx=i, colx=5)+u""
			#note = sh.cell_value(rowx=i, colx=6)+u""
			note = sh.cell_value(rowx=i, colx=5)+u""
			if len(first_name)>0 and len(last_name)>0:
				if no:
					no = int(no)
				else:
					no = None
				try: 
					person = Person.objects.get(no=no)
					person.name_prefix = name_prefix
					person.first_name = first_name
					person.last_name = last_name
					person.organization = organization
					person.note = note
					person.save()
					data.append(person)
				except Person.DoesNotExist:
					person = AddPersonForm({
									'no': no,
									'name_prefix': name_prefix, 
									'first_name': first_name, 
									'last_name': last_name, 
									'organization': organization,
									'note': note,
								})
					person_result = person.save()
					data.append({
						'no': person_result.no,
						'name_prefix': person_result.name_prefix, 
						'first_name': person_result.first_name, 
						'last_name': person_result.last_name, 
						'organization': person_result.organization,
						'note': person_result.note,
						})
	return render(request, 'import_person.html', {'data': data})

def home(request):
	stat = []
	graph = []
	label = []
	log = Log.objects.order_by('timestamp').reverse()
	# Get log stat
	stat_num = log.aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	stat_num = log.filter(timestamp__gte = (date.today()-timedelta(days=6))).aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	stat_num = log.filter(timestamp__gte = (date.today()-timedelta(days=29))).aggregate(Count('timestamp'))
	stat.append(stat_num['timestamp__count'])
	# For graph
	for i in range(0,30):
		day = date.today()-timedelta(days=i)
		stat_num = log.filter(timestamp__year=day.year,
			timestamp__month=day.month,
			timestamp__day=day.day
			).aggregate(Count('timestamp'))
		daystr = date.today()-timedelta(days=i+1)
		graph.append(stat_num['timestamp__count'])
	graph.reverse()
	stat_all = 'จำนวนครั้งที่เข้าทั้งหมด'
	stat_7 = 'จำนวนครั้งที่เข้าภายใน 7 วัน'
	stat_30 = 'จำนวนครั้งที่เข้าภายใน 30 วัน'
	begin_date = date.today()-timedelta(days=30)
	begin_date_arr = [begin_date.strftime('%d'),int(begin_date.strftime('%m'))-1,begin_date.strftime('%Y')]
	return render(request, 'home.html', {
		'stat': stat,
		'begin_date': begin_date_arr,
		'graph': graph,
		'stat_all': stat_all,
		'stat_7': stat_7,
		'stat_30': stat_30,
		'enu_log': enumerate(log[:15]),
		})

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
