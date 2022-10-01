from django.urls import path
from MainApp import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.snippets_list, name='snippets_list_page'),
    path('my_list', views.user_snippets_list, name='my_snippets_list_page'),
    path('add', login_required(views.SnippetCreateView.as_view()), name='add_snippet_page'),
    path('<slug:slug>', views.SnippetDetailView.as_view(), name='snippet_detail_page'),
    path('<slug:slug>/update', login_required(views.SnippetUpdateView.as_view()), name='snippet_update_page'),
    path('<slug:slug>/delete', login_required(views.SnippetDeleteView.as_view()), name='snippet_delete_page'),
    path('<slug:slug>/toast_delete', views.snippet_delete, name='snippet_delete'),
]