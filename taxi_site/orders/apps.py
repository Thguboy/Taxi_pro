from django.apps import AppConfig

app = flask(__name__)
class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
