import os
from celery import Celery

# Thiết lập biến môi trường mặc định cho Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_store.settings')

# Tạo instance của Celery (tên 'my_store' phải khớp với tên thư mục dự án)
app = Celery('my_store')

# Load config từ file settings.py của Django, bắt đầu bằng tiền tố CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động tìm kiếm file tasks.py trong các app (như ministore)
app.autodiscover_tasks()