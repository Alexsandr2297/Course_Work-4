from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import UserCreateView, UserVerifyView, UserListView, UserBlockView
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name

urlpatterns = [
    # Регистрация и верификация
    path('register/', UserCreateView.as_view(), name='register'),
    path('verify/<int:user_id>/<str:email>/', UserVerifyView.as_view(), name='verify'),

    # Вход и выход
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Восстановление пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='password_reset.html', success_url='/users/login/'),
         name='password_reset'),

    # Менеджер: просмотр и блокировка пользователей
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', UserBlockView.as_view(), name='block_user'),
]
