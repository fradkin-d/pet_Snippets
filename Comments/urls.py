from django.urls import path
from . import views


urlpatterns = [
    path('create', views.create_comment, name='create_comment'),
    path('delete/<int:pk>', views.delete_comment, name='delete_comment')
]
