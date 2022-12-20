from django_filters import *
from django_filters.widgets import *
from .models import Post,POSITIONS, Category



class PostFilter(FilterSet):
    #так как хочется получать нормальные названия полей, то я полностью отказался от использования class Meta

    #фильтрация по названию
    post_head = CharFilter(
        field_name='post_head',
        label='Название статьи',
        lookup_expr='icontains'
    )

    #фильтр по категории (новости или статьи)
    post_category = ChoiceFilter(
        field_name='post_category',
        label='Новость или статья',
        lookup_expr='icontains',
        choices=POSITIONS,
        empty_label=''
    )

    #фильтр по дате
    time_in = DateFilter(
        field_name='time_in',
        label='Позже даты',
        lookup_expr='date__gt',
        widget=forms.DateInput(attrs={'type': 'date'}, format=('%Y,%m,%d'))
    )

    category = ModelChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Выберите категорию'

    )
