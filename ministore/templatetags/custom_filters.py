from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Sử dụng: {{ dictionary|get_item:key }}
    Giúp lấy giá trị từ dict bằng key động.
    """
    return dictionary.get(key)