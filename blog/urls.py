# blog/urls.py
from django.urls import path
from .views import * #ShowAllView, ArticleView, RandomArticleView
 
# urlpatterns = [
#     # map the URL (empty string) to the view
#     path('', RandomArticleView.as_view(), name="random"),
#     path('show_all', ShowAllView.as_view(), name="show_all"), # generic class-based view # modified
#     path('article/<int:pk>', ArticleView.as_view(), name='article'), # show one article # new
#     path('article/create', CreateArticleView.as_view(), name="create_article"), # new
# ]
 
urlpatterns = [
    # map the URL (empty string) to the view
	## new view for 'random', refactor 'show_all'
    path('', RandomArticleView.as_view(), name='random'), 
    path('show_all', ShowAllView.as_view(), name='show_all'), 
    path('article/<int:pk>', ArticleView.as_view(), name='article'), 
    path('create_comment', CreateCommentView.as_view(), name='create_comment'), ### FIRST (WITHOUT PK)
    path('article/<int:pk>/create_comment', CreateCommentView.as_view(), name='create_comment'), ### NEW
    path('article/create', CreateArticleView.as_view(), name="create_article"), # new
]
