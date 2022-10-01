from django.urls import path
from . import views


urlpatterns = [
    path('switch_snippetlike/<int:snippet_id>', views.switch_snippetlike, name='switch_snippetlike'),
    path('snippet_non_private/json', views.snippet_json_non_private, name='snippet_non_private_json'),
    path('snippet_user_is_author/json', views.snippet_json_user_is_author, name='snippet_user_is_author_json'),
]

