from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='home'),
    path('vehicles/', views.vehicles_list, name='vehicles'),
    path('buy/<int:pk>/', views.buy_vehicle, name='buy'),
    path('order/<int:order_id>/payment/', views.order_payment_proof, name='order_payment_proof'),
    path('email-debug/', views.email_debug, name='email_debug'),
    path('email-test/', views.email_test, name='email_test'),
    path('support/', views.support_page, name='support'),
    path('support/messages/', views.support_messages_api, name='support_messages_api'),
    path('support/send/', views.support_send_api, name='support_send_api'),
    path('track/', views.track_page, name='track'),
    path('invest/', views.invest_page, name='invest'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
