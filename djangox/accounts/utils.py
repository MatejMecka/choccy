"""
accounts/utils.py

Stellar Related operations for simple use
"""

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, FeeBumpTransaction, ClaimPredicate, Claimant, Asset
server = Server("https://horizon-testnet.stellar.org") # Todo: Not hardcode this?

def getAssets(public_key: str) -> list:
    """
    Get all the balances an account has.
    """
    balances = server.accounts().account_id(public_key).call()['balances']
    balances_to_return = [ {"asset_code": elem.get("asset_code"), "issuer": elem.get("asset_issuer"), "balance": elem.get("balance")} for elem in balances ]
    balances_to_return[-1]["asset_code"] = "XLM"
    return balances_to_return

def getClaimableBalances(public_key: str) -> list:
    """
    Get all the claimable balances an account has to claim.
    """
    balances = server.claimable_balances().for_claimant(public_key).call()['_embedded']['records']
    return [ {"sponsor": elem.get("sponsor"), "id": elem.get("id"), "asset": elem.get("asset").replace('native', 'XLM'), "amount": round(int(float(elem.get("amount"))))} for elem in balances ]

