from django.contrib import admin
from .models import Author,Category,Post,PostCategory,Comment,POSITIONS
from modeltranslation.admin import TranslationAdmin

class PostAdmin(admin.ModelAdmin):
    list_display = ['post_head', 'time_in']

# Register your models here.

class CategoryAdmin(TranslationAdmin):
    model = Category

class PostAdmin(TranslationAdmin):
    model = Post

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
