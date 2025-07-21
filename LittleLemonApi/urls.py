from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    path('groups/manager/users', view= views.ManagerView),
    path('groups/delivery-crew/users', view= views.DeliveyCrewView),
    path('menu-items', view= views.menu_items),
    path('menu-item/<int:id>', view= views.menu_item_single),
    path('cart/menu-items', view = views.cart_view),
    path('orders/<int:orderId>', view = views.order_view_single),
    path('orders', view = views.orders_view),
    path('category', view= views.CategoryList.as_view()),
    path('users', view= views.CategoryList.as_view()),
    path('users/users/me', view= views.CategoryList.as_view()),
    path('auth/login', obtain_auth_token)

]