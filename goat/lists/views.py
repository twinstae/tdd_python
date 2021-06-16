from django.http import HttpResponse
from django.shortcuts import redirect, render
from lists.models import Item, List


def home_page(request):
    return render(request, 'lists/home.html')


def view_list(request, list_id):
    a_list = List.objects.get(id=list_id)
    items = Item.objects.filter(list=a_list)
    return render(request, 'lists/list.html',
                  {
                      'list': a_list
                  })


def new_list(request):
    a_list = List.objects.create()
    new_text = request.POST.get('item_text', '')
    Item.objects.create(text=new_text, list=a_list)
    return redirect(f'/lists/{a_list.id}')


def add_item(request, list_id):
    a_list = List.objects.get(id=list_id)
    new_text = request.POST.get('item_text', '')
    Item.objects.create(text=new_text, list=a_list)
    return redirect(f'/lists/{a_list.id}')
