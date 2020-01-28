from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm,UserForm, UserProfileForm
from django.urls import reverse 



# Create your views here.
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Cruchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list

    #display 5 most viewd webpages
    context_dict['pages'] = sorted(Page.objects.filter(), key=lambda x:x.views , reverse=True)[:5]
    print(context_dict['pages'])
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #context_dict = {'boldmessage':'This tutorial has been put together by nathan.'}
    print(request.method)
    print(request.user)
    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # Can we find a category name slug with the given name? 
        # If we can't, the .get() method raises a DoesNotExist exception. 
        # The .get() method returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)

        # retrieve all of the associated pages
        # the filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages

        # Also add the category object from
        # the database to the context dictionary
        # will be used to versify that category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # This is called if we didnt find the specified category
        # Let the template display 'no category' for us
        context_dict['category'] = None
        context_dict['pages'] = None

    # render response and return it to the client
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)

            # possibly incorrect syntax here
            return redirect('rango:index')#reverse('rango:index'))
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    if category is None:
        return redirect('rango:index')
    
    form = PageForm()
    if request.method == 'POST':
        form.PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))        
        else:
            print(form.errors)
    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # bool value for telling the template 
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # If its a HTTP POST, we'ew interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab info from the raw form info
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save form data in DB
            user = user_form.save()

            # save the password with set_password method.
            # this creates a hash

            user.set_password(uesr.password)
            user.save()

            # sort out user profile instance
            