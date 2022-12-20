from django.urls import path
# Импортируем созданное нами представление
from .views import PostList,PostDetail,PostCreate,PostUpdate,PostDelete,subscribe_me,PostCount, upgrade_me, notsubscribe_me


urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('news/create/', PostCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/create/', PostCreate.as_view(), name='post_create'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('subscribe/', subscribe_me, name='subscribe'),
    path('notsubscribe/', notsubscribe_me, name='notsubscribe'),
    path('post_count/', PostCount.as_view(), name='post_count'),
    path('upgrade/', upgrade_me, name='upgrade')
    ]