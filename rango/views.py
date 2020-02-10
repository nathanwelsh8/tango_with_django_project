from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm,UserForm, UserProfileForm
from django.urls import reverse 
from datetime import datetime


# Create your views here.
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Cruchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list

    #display 5 most viewd webpages
    context_dict['pages']  = sorted(Page.objects.filter(), key=lambda x:x.views , reverse=True)[:5]
    visitor_cookie_handler(request)
    
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    #context_dict = {'boldmessage':'This tutorial has been put together by nathan.'}
    print(request.method)
    print(request.user)
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    context_dict = {}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/about.html', context=context_dict)
    
    return response

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

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    # You cannot add a page to a Category that DNE
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)  
    
    context_dict = {'form': form, 'category': category}
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

            user.set_password(user.password)
            user.save()

            # sort out user profile instance
            """One trick we use here that has caught many people out in the past
             is the use of commit=False when saving the UserProfileform.
             This stops Django from saving the data to the database in the first instance.
             Why do this? Remember that information from the UserProfileForm form is
            passed onto a new instance of the UserProfile model.
            The UserProfile contains a foreign key reference to the standard 
            Django User model – but the UserProfile does not provide this information!
            Attempting to save the new instance in an incomplete state would raise a 
            referential integrity error.The link between the two models is required. 
           """
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did usr provide profile pic?
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            #save the UserProfile model instance
            profile.save()
            
            # Indicate that the template registration
            # was successful
            registered = True

        else:
            #Print errors
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,
                    'rango/register.html',
                    # the data which the webpage can interact with
                    context = {'user_form':user_form,
                    'profile_form': profile_form,
                    'registered': registered})

def user_login(request):
    if request.method =='POST':
        # Gather the username and password provided by the user. 
        # This information is obtained from the login form. 
        # We use request.POST.get('<variable>') as opposed 
        # to request.POST['<variable>'], because the 
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>'] 
        # will raise a KeyError exception. 
        username = request.POST.get('username')
        password = request.POST.get('password')

        # returns a user object if deets are correct
        user = authenticate(username=username, password=password)

        if user:

            #if account is active
            if user.is_active:
                # if the account is valid and active we can log the user in
                # send them to the homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account has been disabled")
        else:
            # Bad login details
            print(f"Invalid Login details:{username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    # request is not a POST
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

###    Helper Functions ###
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get the number of visits to the site. 
    # We use the COOKIES.get() function to obtain the visits cookie. 
    # If the cookie exists, the value returned is casted to an integer. 
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request,'visits','1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    # if its been more than a day since last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits +=1 # possible error in autobot : visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set last visit cookie
        request.session['last_visit']=  last_visit_cookie
    # UPDATE/SET the visits cookie
    request.session['visits'] = visits
