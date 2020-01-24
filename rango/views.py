from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page


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
    context_dict = {'boldmessage':'This tutorial has been put together by nathan.'}
    return render(request, 'rango/about.html', context_dict)

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
