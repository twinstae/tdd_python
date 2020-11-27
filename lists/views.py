from django.http import HttpResponse
from django.shortcuts import redirect, render
from lists.models import Item


def home_page(request):
    if request.method == "POST":
        new_text = request.POST.get('item_text', '')
        Item.objects.create(text=new_text)
        return redirect('/')

    return render(
        request,
        'lists/home.html',
        {'item_list': Item.objects.all()}
    )
