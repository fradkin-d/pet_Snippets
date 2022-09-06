"""pet_Snippets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MainApp import views as main_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index_page, name='home'),
    path('registration', main_views.registration, name='registration'),
    path('login', main_views.login, name='login'),
    path('logout', main_views.logout, name='logout'),
    path('snippets/add', main_views.SnippetCreateView.as_view(), name='add_snippet_page'),
    path('snippets/list', main_views.snippets_list, name='snippets_list_page'),
    path('snippets/my_list', main_views.user_snippets_list, name='my_snippets_list_page'),
    path('snippets/<slug:slug>', main_views.SnippetDetailView.as_view(), name='snippet_detail_page'),
    path('snippets/<slug:slug>/update', main_views.SnippetUpdateView.as_view(), name='snippet_update_page'),
    path('snippets/<slug:slug>/delete', main_views.SnippetDeleteView.as_view(), name='snippet_delete_page'),
    path('comment/create', main_views.create_comment, name='create_comment'),
    path('comment/delete/<int:pk>', main_views.delete_comment, name='delete_comment'),
    path('ajax/switch_snippetlike/<int:snippet_id>', main_views.switch_snippetlike, name='switch_snippetlike'),
    path('ajax/snippet_non_private/json', main_views.snippet_json_non_private, name='snippet_non_private_json'),
    path('ajax/snippet_user_is_author/json', main_views.snippet_json_user_is_author, name='snippet_user_is_author_json'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

