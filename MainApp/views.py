from django.shortcuts import render


def index_page(request):
    context = {'pagename': 'Snippets'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    context = {'pagename': 'Добавление нового сниппета'}
    return render(request, 'pages/add_snippet.html', context)


def snippets_list_page(request):
    context = {'pagename': 'Просмотр сниппетов'}
    return render(request, 'pages/view_snippets.html', context)
