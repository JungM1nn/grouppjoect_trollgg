from django.shortcuts import render, redirect, get_object_or_404
from .models import Article
from .forms import ArticleForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST

def index(request):
    return render(request, "index.html")

def users(request):
    return render(request, "users.html")


def data_throw(request):
    return render(request, "data_throw.html")

def data_catch(request):
    message = request.GET.get("message")
    context = {"message": message}
    return render(request, "data_catch.html", context)

def profile(request, username):
    context = {
        "username": username

    }
    return render(request, "profile.html", context)

def articles(request):
    articles = Article.objects.all().order_by('-pk')
    context = {
        "articles": articles,
    }
    return render(request, "articles.html", context)

@login_required
def create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            return redirect('article_detail', article.pk)
    else:
        form = ArticleForm()

    context = {'form': form}
    return render(request, 'create.html', context)


    # title = request.POST.get('title')
    # content = request.POST.get('content')
    # article = Article.objects.create(title=title, content=content)
    # return redirect('article_detail', article.pk)

def update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            return redirect("article_detail", article.pk)
        
    else:
        form = ArticleForm(instance=article)
    
    context = {
        "form": form,
        "article": article,
        }
    return render(request, "update.html", context)


@require_POST
def delete(request, pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=pk)
        article.delete()
    return redirect("articles:articles")

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    context = {"article": article}
    return render(request, "article_detail.html", context)
