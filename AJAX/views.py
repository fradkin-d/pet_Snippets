import math

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse

from AJAX.models import SnippetLike
from MainApp.models import Snippet


def snippets_json(request, username=''):
    search = request.GET.get('search[value]')
    order_i = request.GET.get('order[0][column]')
    order_col = request.GET.get(f'columns[{order_i}][data]')
    order_dir = request.GET.get('order[0][dir]')
    start = request.GET.get('start')
    length = request.GET.get('length')

    sql = f'''
    WITH vars(search_var) AS (values('{search if search else ""}%')) 
    SELECT 
        s.name AS name, 
        s.lang_id AS lang, 
        COUNT(DISTINCT sl.id) AS like_count, 
        COUNT(DISTINCT c.id) AS comment_count, 
        {"s.is_private AS is_private" if username else "u.username AS author"}, 
        s.creation_date AS creation_date, 
        s.slug AS slug 
    FROM "MainApp_snippet" AS s 
    LEFT OUTER JOIN "Comments_comment" AS c ON s.id = c.snippet_id 
    LEFT OUTER JOIN "AJAX_snippetlike" AS sl ON s.id = sl.snippet_id 
    LEFT OUTER JOIN "auth_user" AS u ON s.author_id = u.id, 
    vars {f"WHERE u.username = '{username}'" if username else "WHERE s.is_private = FALSE"} 
    GROUP BY s.id, u.username, vars.search_var 
    HAVING s."name" LIKE vars.search_var 
        OR s.lang_id  LIKE vars.search_var 
        OR u.username LIKE vars.search_var 
    ORDER BY {order_col if order_col else 'creation_date'} {order_dir if order_dir else 'desc'}
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        data = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    response = {
        'data': data,
        'recordsTotal': Snippet.objects.all().count(),
        'recordsFiltered': len(data)
    }

    if start and length:
        response.update({
            'data': data[int(start):int(start) + int(length)],
            'page': math.ceil(int(start) / int(length)) + 1,
            'per_page': int(length),
        })
    # pp(connection.queries)
    return JsonResponse(response)


def snippet_json_non_private(request):
    return snippets_json(request)


@login_required
def snippet_json_user_is_author(request):
    return snippets_json(request, request.user.username)


def switch_snippetlike(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    response = {
        'was_liked': SnippetLike.objects.filter(snippet=snippet, author=request.user).exists()
    }
    if response['was_liked']:
        SnippetLike.objects.filter(snippet=snippet, author=request.user).delete()
    else:
        SnippetLike.objects.create(snippet=snippet, author=request.user)
    return JsonResponse(response)
