from django import template


register = template.Library()

list_mat = ['редиска', 'чмо', 'хер', 'фиг', 'говно']


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def censor(value):
    for i in list_mat:
        value = value.replace(i, i[0] + ('*' * (len(i) - 1)))
        value = value.replace(i.capitalize(), i[0].capitalize() + ('*' * (len(i) - 1)))

    # Возвращаемое функцией значение подставится в шаблон.
    return f'{value}'