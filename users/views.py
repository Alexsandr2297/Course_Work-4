from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from users.forms import UserRegisterForm
from mailmaster.models import Mailing


class UserCreateView(CreateView):
    """Регистрация пользователя с подтверждением email."""
    model = User
    form_class = UserRegisterForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Неактивен до подтверждения
        user.save()

        # Создаем ссылку для подтверждения
        verify_url = self.request.build_absolute_uri(
            reverse_lazy('users:verify', args=[user.id, user.email])
        )

        # Отправляем письмо
        try:
            send_mail(
                subject='Подтверждение регистрации',
                message=f'Для подтверждения регистрации перейдите по ссылке: {verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(self.request, 'Регистрация успешна! На вашу почту отправлена ссылка для подтверждения.')
        except Exception as e:
            messages.error(self.request, f'Ошибка отправки письма: {e}')
            user.is_active = True  # Активируем вручную при ошибке
            user.save()

        return super().form_valid(form)


class UserVerifyView(View):
    """Подтверждение email пользователя."""
    def get(self, request, user_id, email):
        try:
            user = User.objects.get(id=user_id, email=email)
            user.is_active = True
            user.save()
            messages.success(request, 'Email подтвержден! Теперь вы можете войти.')
        except User.DoesNotExist:
            messages.error(request, 'Неверная ссылка подтверждения.')
        return redirect('users:login')


class UserListView(LoginRequiredMixin, ListView):
    """Список пользователей (только для менеджеров)."""
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('users.can_view_users'):
            return HttpResponseForbidden("У вас нет прав для просмотра этой страницы")
        return super().dispatch(request, *args, **kwargs)


class UserBlockView(LoginRequiredMixin, View):
    """Блокировка/разблокировка пользователя (только для менеджеров)."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('users.can_block_user'):
            return HttpResponseForbidden("У вас нет прав для блокировки пользователей")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        messages.success(request,
                         f"Пользователь {user.email} {'заблокирован' if not user.is_active else 'разблокирован'}")
        return redirect('users:user_list')


class DisableMailingView(LoginRequiredMixin, View):
    """Отключение рассылки (только для менеджеров)."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('mailmaster.can_disable_mailing'):
            return HttpResponseForbidden("У вас нет прав для отключения рассылок")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        messages.success(request, f"Рассылка #{mailing.id} отключена")
        return redirect('mailmaster:mailing_detail', pk=pk)