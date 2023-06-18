from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/<int:id>', views.chitiet, name='blog'),
    path('blog/<int:id>/edit', views.editBlog, name='edit'),
    path('blogs', views.blogs, name='blogs'),
    path('collection/<int:id>', views.conllection, name='collection'),
    path('@<str:username>', views.profile, name='profile'),
    path('@<str:username>/edit', views.editProfile, name='editProfile'),
    path('about', views.about, name='about'),
    path('more', views.more, name='more'),
    path('create', views.createBlog, name='create'),
    path('search', views.search, name='search'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('reaction/<int:blogId>/', views.reaction, name='reaction'),
    path('comment/<int:blogId>/', views.comment, name='comment'),
    path('random', views.random, name='random'),
    path('admin', views.admin, name='admin'),
    path('rank/<str:period>', views.ranking, name='rank'),
    path('manage', views.manage, name='manage'),
]
