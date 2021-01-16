"""
accounts/utils.py

Stellar Related operations for simple use
"""

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, FeeBumpTransaction, ClaimPredicate, Claimant, Asset
import os
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

def generateAccount() -> dict:
    """
    Generate an Account for a User who never made an account with Stellar
    """
    keypair = Keypair.random()

    public_account = os.environ["STELLAR_PUBLIC_KEY"]
    private_key = os.environ["STELLAR_PRIVATE_KEY"]
    
    
    base_fee = server.fetch_base_fee()*3
    account = server.load_account(public_account)

    transaction = TransactionBuilder(
        source_account=account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    ).append_begin_sponsoring_future_reserves_op(
        sponsored_id=keypair.public_key,
        source=public_account
    ).append_create_account_op(
        destination=keypair.public_key,
        starting_balance="0",
        source=public_account
    ).append_end_sponsoring_future_reserves_op(
        source=keypair.public_key
    ).build()

    print(transaction.to_xdr())

    transaction.sign(private_key)
    transaction.sign(keypair.secret)
    response = server.submit_transaction(transaction)

    print(response)

    return {"public_key": keypair.public_key, "private_key": keypair.secret}