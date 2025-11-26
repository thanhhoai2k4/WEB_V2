from django import template
import pprint

register = template.Library()

@register.filter
def debug_object(value):
    """
    Filter này giúp in ra toàn bộ thuộc tính của object lên màn hình HTML
    để soi xét.
    Cách dùng trong HTML: {{ some_variable|debug_object }}
    """
    try:
        # Lấy tất cả thuộc tính của object dưới dạng dict
        d = vars(value)
        return pprint.pformat(d)
    except TypeError:
        # Nếu không phải object (ví dụ list, string), in trực tiếp
        return pprint.pformat(value)