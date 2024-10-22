from django.urls import path
from .views import check_token_holders, add_wallet, wallet_list_delete

urlpatterns = [
    path('api/search/<str:contract_address>/', check_token_holders, name='check_token_holders'),
    path('api/wallets/', add_wallet, name='add_wallet'),  # POST for adding wallets
    path('api/wallets/<str:wallet_address>/', wallet_list_delete, name='wallet_delete'),  # DELETE for removing a wallet
]
