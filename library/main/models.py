from django.contrib.auth.models import User
from django.db import models

# Create your models here.



class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.CharField(max_length=100)
    publisher = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Reader(models.Model):

    ROLE_CHOICES = [
        ('reader', 'Читач'),
        ('librarian', 'Бібліотекар'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    registration_date = models.DateField(auto_now_add=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader'
    )

    def __str__(self):
        return f"{self.name} {self.surname}"


class BookCopy(models.Model):

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='copies'
    )

    reader = models.ForeignKey(
        Reader,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_copies'
    )

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.name} — примірник №{self.id}"