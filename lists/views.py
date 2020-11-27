from django.http import HttpResponse
from django.shortcuts import redirect, render
from lists.models import Item, List


def home_page(request):
    return render(request, 'lists/home.html')


def view_list(request):
    items = Item.objects.all()
    return render(request, 'lists/list.html', {'item_list': items})


def new_list(request):
    a_list = List.objects.create()
    new_text = request.POST.get('item_text', '')
    Item.objects.create(text=new_text, list=a_list)
    return redirect('/lists/the-only-list-in-the-world')
