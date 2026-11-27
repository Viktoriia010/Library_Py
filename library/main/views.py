from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .models import Book, Reader, BookCopy
from django.db import connection
import os
from django.contrib.auth import authenticate, login, logout, get_user_model

User = get_user_model()


# Create your views here.

def home(request):
    # user = User.objects.create_user(
    #     username='librarian',
    #     password='Library123'
    # )
    #
    # Reader.objects.create(
    #     user=user,
    #     name='Анна',
    #     surname='Коваленко',
    #     email='librarian@gmail.com',
    #     phone='+380501234567',
    #     role='librarian'
    # )

    books = Book.objects.annotate(
        available_copies=Count(
            'copies',
            filter=Q(copies__is_available=True)
        ),
        total_copies=Count('copies')
    )

    if request.GET.get('filter') == 'available':
        books = books.filter(available_copies__gt=0)

    search = request.GET.get('search')

    if search:
        books = books.filter(
            Q(name__icontains=search) |
            Q(author__icontains=search)
        )

    info = {
        'books': books,
        'available_books': BookCopy.objects.filter(
            is_available=True
        ).count(),
        'borrowed_books': BookCopy.objects.filter(
            is_available=False
        ).count(),
        'total_readers': Reader.objects.count()
    }

    return render(request, 'main/index.html', {
        'info': info
    })

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'main/register.html', {
                'error': 'Паролі не збігаються'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'main/register.html', {
                'error': 'Такий логін вже існує'
            })

        if Reader.objects.filter(email=email).exists():
            return render(request, 'main/register.html', {
                'error': 'Такий email вже зареєстрований'
            })

        if len(password) < 8:
            return render(request, 'main/register.html', {
                'error': 'Пароль повинен містити мінімум 8 символів'
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Reader.objects.create(
            user=user,
            name=name,
            surname=surname,
            email=email,
            phone=phone,
            role='reader'
        )

        reader_group, created = Group.objects.get_or_create(name='Читачі')

        user.groups.add(reader_group)

        login(request, user)

        return redirect('/')

    return render(request, 'main/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/')

        return render(request, 'main/login.html', {
            'error': 'Неправильний логін або пароль'
        })

    return render(request, 'main/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def librarian_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        reader = Reader.objects.filter(
            user=request.user
        ).first()

        if not reader or reader.role != 'librarian':
            return redirect('index')

        return view_func(request, *args, **kwargs)

    return wrapper



@login_required
@librarian_required
def give_book(request, book_id):

    copy = BookCopy.objects.get(id=book_id)

    if request.method == 'POST':
        reader_id = request.POST.get('reader_id')

        reader = Reader.objects.get(id=reader_id)

        if copy.is_available:
            copy.reader = reader
            copy.is_available = False
            copy.save()

    return redirect('loans')




@login_required
@librarian_required
def return_book(request, book_id):

    copy = BookCopy.objects.get(id=book_id)

    copy.reader = None
    copy.is_available = True
    copy.save()

    return redirect('loans')


@login_required
@librarian_required
def readers_list(request):

    readers = Reader.objects.prefetch_related(
        'book_copies__book'
    )

    return render(request, 'main/readers.html', {
        'readers': readers
    })

@login_required
@librarian_required
def borrowed_books(request):

    borrowed_copies = BookCopy.objects.filter(
        is_available=False
    ).select_related('book', 'reader')

    return render(request, 'main/loans.html', {
        'borrowed_copies': borrowed_copies,
        'borrowed_books': borrowed_copies.count(),
        'readers_with_books': borrowed_copies.values(
            'reader'
        ).distinct().count()
    })

def book_detail(request, book_id):

    book = Book.objects.prefetch_related(
        'copies__reader'
    ).get(id=book_id)

    copies = book.copies.all()

    return render(request, 'main/book_detail.html', {
        'book': book,
        'copies': copies,
        'total_copies': copies.count(),
        'readers': Reader.objects.all(),
        'available_copies': copies.filter(
            is_available=True
        ).count()
    })

@login_required
@librarian_required
def reader_detail(request, reader_id):

    reader = Reader.objects.prefetch_related(
        'book_copies__book'
    ).get(id=reader_id)

    return render(request, 'main/reader_detail.html', {
        'reader': reader
    })


@login_required
@librarian_required
def add_book(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        author = request.POST.get('author')
        year = request.POST.get('year')
        genre = request.POST.get('genre')
        publisher = request.POST.get('publisher')

        try:
            copies_count = int(
                request.POST.get('copies_count', 1)
            )

            year = int(year)

            if copies_count < 1 or not 1 <= year <= 2100:
                raise ValueError

        except (ValueError, TypeError):
            return render(request, 'main/books_add.html', {
                'error': 'Перевір рік видання та кількість примірників'
            })

        book = Book.objects.create(
            name=name,
            author=author,
            year=year,
            genre=genre,
            publisher=publisher
        )

        BookCopy.objects.bulk_create([
            BookCopy(book=book)
            for _ in range(copies_count)
        ])

        return redirect('home')

    return render(request, 'main/books_add.html')