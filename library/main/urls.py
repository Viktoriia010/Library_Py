from django.urls import path, include

from . import  views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('readers/', views.readers_list, name='readers'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('loans/', views.borrowed_books, name='loans'),
    path('readers/<int:reader_id>/',views.reader_detail,name='reader_detail'),
    path('book/<int:book_id>/give/',views.give_book,name='give_book'),
    path('book/<int:book_id>/return/',views.return_book,name='return_book'),
    path('books/add/',views.add_book,name='add_book'),
]