from django.urls import path
from .views import search_contract_interactions, add_wallet, wallet_list_delete

urlpatterns = [
    path('api/search/<str:contract_address>/', search_contract_interactions, name='search_contract_interactions'),
    path('api/wallets/', add_wallet, name='add_wallet'),  # POST for adding wallets
    path('api/wallets/<str:wallet_address>/', wallet_list_delete, name='wallet_delete'),  # DELETE for removing a wallet
]
