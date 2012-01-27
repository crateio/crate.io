from django import template

register = template.Library()


@register.filter
def paginate_numbers(numbers, current_page, max_num=13):
    step = (max_num - 1) / 2
    start = numbers.index(current_page) - step

    if start < 0:
        end = numbers.index(current_page) + step + abs(start)
        start = 0
    else:
        end = numbers.index(current_page) + step
    return numbers[start:end + 1]
