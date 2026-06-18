from django.urls import path
from mailmaster.apps import MailmasterConfig
from mailmaster.views import (
    RecipientListView, RecipientDetailView, RecipientCreateView,
    RecipientUpdateView, RecipientDeleteView,
    MessageListView, MessageDetailView, MessageCreateView,
    MessageUpdateView, MessageDeleteView,
    MailingListView, MailingDetailView, MailingCreateView,
    MailingUpdateView, MailingDeleteView,
    SendMailingView, DisableMailingView
)

app_name = MailmasterConfig.name

urlpatterns = [
    # Главная страница
    path('', MailingListView.as_view(), name='mailmaster_list'),

    # Recipient URLs
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    # Message URLs
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # Mailing URLs
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', SendMailingView.as_view(), name='send_mailing'),
    path('mailings/<int:pk>/disable/', DisableMailingView.as_view(), name='disable_mailing'),
]