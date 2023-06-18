from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username', 'email','updatedat']
    readonly_fields = ['id']
    list_filter = ['updatedat']
    search_field = ['username','email']

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id','title','updatedat']
    readonly_fields = ['id']
    list_filter = ['updatedat']
    search_field = ['title']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=['id','content']
    readonly_fields = ['id']
    search_fields=['content']

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display=['id','reaction']
    readonly_fields = ['id']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display=['id','name']
    readonly_fields = ['id']
    search_fields=['name']