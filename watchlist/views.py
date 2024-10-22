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


ERC20_ABI = '''
[
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "type": "function"
    }
]
'''



@api_view(['GET'])
def check_token_holders(request, contract_address):
    result_list = []

    try:

        # Initialize Web3 connection
        w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{config("INFURA_APP_ID")}'))

        # Create a contract instance for the token
        token_contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ERC20_ABI)

        # Fetch wallets tagged "Watchlist"
        wallets = Wallet.objects.filter(tag="Watchlist")

        for wallet in wallets:
            # Fetch the balance of the wallet for the given token
            balance = token_contract.functions.balanceOf(wallet.address).call()

            # Convert balance to a readable format (assuming the token has 18 decimals like most ERC-20 tokens)
            token_balance = w3.from_wei(balance, 'ether')

            serialized_wallet = WalletSerializer(wallet).data
            serialized_wallet['tokenBalance'] = token_balance
            serialized_wallet['hasToken'] = token_balance > 0
            result_list.append(serialized_wallet)

        return Response(result_list)
    except:
        return Response({'error': 'An error occured'}, status=status.HTTP_500_SERVER_ERROR)


@api_view(['GET', 'POST', 'PUT'])
def add_wallet(request):
    if request.method == 'GET':
        wallets = Wallet.objects.all()
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        wallet_address = request.data.get('address')
        
        if wallet_address:
            if Wallet.objects.filter(address=wallet_address).exists():
                return Response({'error': 'Wallet already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            wallet = Wallet(address=wallet_address)
            wallet.save()
            return Response({'message': 'Wallet added successfully'}, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        wallet_address = request.data.get('address')
        tag = request.data.get('tag')
        
        if wallet_address:
            try:
                wallet = Wallet.objects.get(address=wallet_address)
                wallet.tag = tag
                wallet.save()
                return Response({'message': 'Wallet tag updated successfully'}, status=status.HTTP_200_OK)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def wallet_list_delete(request, wallet_address=None):
    if request.method == 'DELETE':
        wallet = Wallet.objects.filter(address=wallet_address).first()
        if wallet:
            wallet.delete()
            return Response({'message': 'Wallet deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
