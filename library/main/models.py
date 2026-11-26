from django.db import models

# Create your models here.


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    publisher = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class Reader(models.Model):
    ROLE_CHOICES = [
        ('reader', 'Читач'),
        ('librarian', 'Бібліотекар'),
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    registration_date = models.DateField(auto_now_add=True)
    books = models.ManyToManyField(Book, blank=True)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='reader')

    def __str__(self):
        return f"{self.name} {self.surname}"