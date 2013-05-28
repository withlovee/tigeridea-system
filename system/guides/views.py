from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from guides.forms import AddPersonForm
from guides.models import Person, BannedPerson

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
		form = AddPersonForm(request.POST)
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
    success_url = '/list/'

class UnbanPerson(DeleteView):
    model = BannedPerson
    slug_field = 'name__no'
    template_name = 'unban_person.html'
    success_url = '/banned/'