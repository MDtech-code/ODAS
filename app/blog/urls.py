from django.urls import path
from . import views
urlpatterns = [
    path("", views.ArticleListView.as_view(), name="article_list"),
    path("article/<int:pk>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("create/", views.ArticleCreateView.as_view(), name="article_create"),
    path("update/<int:pk>/", views.ArticleUpdateView.as_view(), name="article_update"),
    path("delete/<int:pk>/", views.ArticleDeleteView.as_view(), name="article_delete"),
    path('article/<int:article_id>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),  # New URL for adding comments
    path('comments/moderate/', views.CommentModerationView.as_view(), name='comment_moderation'),
    path('comments/<int:pk>/approve/', views.ApproveCommentView.as_view(), name='approve_comment'),
    path('comments/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),    
    
]
