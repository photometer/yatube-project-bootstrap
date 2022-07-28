from django.contrib import admin
from .models import Post, Group, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
    )
    search_fields = ('title',)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
