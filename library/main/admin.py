from django.contrib import admin

from .models import Reader, Book, BookCopy

# Register your models here.

admin.site.register(Reader)
admin.site.register(Book)
admin.site.register(BookCopy)
