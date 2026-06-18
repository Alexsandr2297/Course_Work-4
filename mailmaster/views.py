from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Recipient, Message, Mailing
from .forms import RecipientForm, MessageForm, MailingForm
from .services import MailingService, get_global_stats, get_mailing_stats


#                Получатель
class RecipientListView(LoginRequiredMixin, ListView):
    """Список получателей текущего пользователя."""
    model = Recipient
    template_name = 'mailmaster_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание получателя с автоматическим назначением владельца."""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя (только для владельца)."""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def dispatch(self, request, *args, **kwargs):
        recipient = self.get_object()
        if request.user != recipient.owner:
            messages.error(request, "У вас нет прав для редактирования этого получателя.")
            return redirect('mailmaster:mailmaster_list')
        return super().dispatch(request, *args, **kwargs)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр получателя."""
    model = Recipient
    template_name = 'mailmaster_detail.html'
    context_object_name = 'recipient'


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя (только для владельца)."""
    model = Recipient
    template_name = 'mailmaster_confirm_delete.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def dispatch(self, request, *args, **kwargs):
        recipient = self.get_object()
        if request.user != recipient.owner:
            messages.error(request, "У вас нет прав для удаления этого получателя.")
            return redirect('mailmaster:mailmaster_list')
        return super().dispatch(request, *args, **kwargs)


#                  Сообщение
class MessageListView(LoginRequiredMixin, ListView):
    """Список всех сообщений."""
    model = Message
    template_name = 'mailmaster_list.html'
    context_object_name = 'messages'


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр сообщения."""
    model = Message
    template_name = 'mailmaster_detail.html'
    context_object_name = 'message'


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения."""
    model = Message
    template_name = 'mailmaster_confirm_delete.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')


#           Рассылки
class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок с кешированием."""
    model = Mailing
    template_name = 'mailmaster_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('mailmaster.can_view_all'):
            return MailingService.get_all_mailings()
        return MailingService.get_user_mailings(user.id)


@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр рассылки с кешированием страницы."""
    model = Mailing
    template_name = 'mailmaster_detail.html'
    context_object_name = 'mailing'

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        user = request.user
        if mailing.owner != user and not user.has_perm('mailmaster.can_view_all') and not user.is_staff:
            messages.error(request, "У вас нет доступа к этой рассылке.")
            return redirect('mailmaster:mailmaster_list')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all()[:50]
        context['stats'] = get_mailing_stats(self.object)
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки с очисткой кеша."""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        # Очищаем кеш
        cache.delete(f'mailings_user_{self.request.user.id}')
        cache.delete('mailings_all')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки (только для владельца)."""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailmaster_form.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if request.user != mailing.owner:
            messages.error(request, "У вас нет прав для редактирования этой рассылки.")
            return redirect('mailmaster:mailmaster_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Очищаем кеш
        cache.delete(f'mailings_user_{self.request.user.id}')
        cache.delete('mailings_all')
        cache.delete(f'mailing_{self.object.pk}')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки (только для владельца)."""
    model = Mailing
    template_name = 'mailmaster_confirm_delete.html'
    success_url = reverse_lazy('mailmaster:mailmaster_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if request.user != mailing.owner:
            messages.error(request, "У вас нет прав для удаления этой рассылки.")
            return redirect('mailmaster:mailmaster_list')
        return super().dispatch(request, *args, **kwargs)


class SendMailingView(LoginRequiredMixin, View):
    """Запуск рассылки по требованию (GET и POST)."""
    def get(self, request, pk):
        return self.post(request, pk)  # перенаправляем на post

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        messages.success(request, mailing.send_mailing())
        return redirect('mailmaster:mailing_detail', pk=pk)


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


class HomeView(LoginRequiredMixin, TemplateView):
    """Главная страница со статистикой."""
    template_name = 'mailmaster_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_global_stats())
        return context
