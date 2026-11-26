from django.shortcuts import render

from .models import Book, Reader


# Create your views here.

def home(request):
    return render(request, 'main/index.html', {'books': Book.objects.all()})

def readers(request):
    return render(request, 'main/readers.html', {'readers': Reader.objects.all()})

def books_in_reader(request, reader_id):
    books =[]
    if reader_id:
        reader = Reader.objects.get(id=reader_id)
        books = reader.books.all()
    return render(request, 'main/resders.html', {'books_by_reader': books})