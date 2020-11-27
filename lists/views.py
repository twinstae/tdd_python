from django.http import HttpResponse
from django.shortcuts import redirect, render
from lists.models import Item


def home_page(request):
    if request.method == "POST":
        new_text = request.POST.get('item_text', '')
        Item.objects.create(text=new_text)
        return redirect('/lists/the-only-list-in-the-world')

    return render(
        request,
        'lists/home.html',
        {'item_list': Item.objects.all()}
    )


def view_list(request):
    items = Item.objects.all()
    return render(request, 'lists/list.html', {'item_list': items})
