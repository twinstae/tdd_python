from django.http import HttpResponse
from django.shortcuts import render


def home_page(request):
    if 'item_text' not in request.POST:
        print(request.POST)

    return render(
        request,
        'lists/home.html',
        {'new_item_text': request.POST.get('item_text', '')}
    )
