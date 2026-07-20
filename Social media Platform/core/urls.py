from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/follow/<int:profile_id>/', views.follow_unfollow, name='follow_unfollow'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    # Messaging/Conversations
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/send/<str:username>/', views.send_message, name='send_message'),
    path('messages/get/<str:username>/', views.get_messages, name='get_messages'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
