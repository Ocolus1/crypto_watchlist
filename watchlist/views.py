# watchlist/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Wallet
from .serializers import WalletSerializer
from rest_framework import status
from web3 import Web3
import requests
from decouple import config

ETHERSCAN_API_KEY = config("ETHERSCAN_API_KEY")


def get_transaction_history(address):
    """
    Uses Etherscan API to fetch transaction history for an Ethereum address.
    """
    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=asc&apikey={ETHERSCAN_API_KEY}'
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == '1' and data['message'] == 'OK':
        return data['result']
    else:
        print(f"Error fetching transactions: {data.get('message', 'Unknown error')}")
        return []



@api_view(['GET'])
def search_contract_interactions(request, contract_address):
    result_list = []

    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{config("INFURA_APP_ID")}'))  # You need an Infura project ID
    wallets = Wallet.objects.all()

    for wallet in wallets:
        has_interacted = False

        # Fetch transaction history using Etherscan
        transactions = get_transaction_history(wallet)
        
        for tx in transactions:
            if tx['to'].lower() == contract_address.lower():
                has_interacted = True
                break

        serialized_wallet = WalletSerializer(wallet).data
        serialized_wallet['hasInteracted'] = has_interacted
        result_list.append(serialized_wallet)

    return Response(result_list)


@api_view(['GET', 'POST'])
def add_wallet(request):
    if request.method == 'GET':
        wallets = Wallet.objects.all()
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        wallet_address = request.data.get('address')
        
        if wallet_address:
            # Check if wallet already exists
            if Wallet.objects.filter(address=wallet_address).exists():
                return Response({'error': 'Wallet already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create new wallet entry
            wallet = Wallet(address=wallet_address)
            wallet.save()

            return Response({'message': 'Wallet added successfully'}, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def wallet_list_delete(request, wallet_address=None):
    if request.method == 'DELETE':
        wallet = Wallet.objects.filter(address=wallet_address).first()
        if wallet:
            wallet.delete()
            return Response({'message': 'Wallet deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)