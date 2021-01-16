"""
accounts/utils.py

Stellar Related operations for simple use
"""

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, FeeBumpTransaction, ClaimPredicate, Claimant, Asset, exceptions
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
    return [ {"sponsor": elem.get("sponsor"), "id": elem.get("id"), "asset": elem.get("asset").replace('native', 'XLM').split(':')[0], "amount": round(int(float(elem.get("amount"))))} for elem in balances ]

def getClaimableBalance(id: str) -> dict:
    """
    Get a claimable balances by id.
    """
    balance = server.claimable_balances().claimable_balance(id).call()
    return {"asset": balance.get("asset").split(':'), "amount": balance.get('amount')}

def claimBalance(id: str, private_key: str, asset=None, asset_issuer=None):
    """
    Claim a Claimable balance
    """
    user_keypair = None
    try:
        user_keypair = Keypair.from_secret(private_key)
    except exceptions.Ed25519SecretSeedInvalidError:
        return False, "Private key is invalid"

    user_pub_key = user_keypair.public_key
    base_fee = server.fetch_base_fee()*3
    account = server.load_account(user_pub_key)
    transaction = None

    if asset == None and asset_issuer == None:
        transaction = TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE
        ).append_claim_claimable_balance_op(
            balance_id=id,
            source=user_pub_key
        ).build()
    else:
        
        transaction = TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE
        ).append_change_trust_op(
            asset_code=asset, 
            asset_issuer=asset_issuer
        ).append_claim_claimable_balance_op(
            balance_id=id,
            source=user_pub_key
        ).build()
    try:
        transaction.sign(private_key)
        print(transaction.to_xdr())
        response = server.submit_transaction(transaction)
        print(response)
    except exceptions.NotFoundError:
        return False, "No Claimable balance has been found"
    except:
        our_keypair = Keypair.from_secret(os.environ["STELLAR_PRIVATE_KEY"])
        fee_bump_tx = TransactionBuilder.build_fee_bump_transaction(
            fee_source=our_keypair, 
            base_fee=base_fee, 
            inner_transaction_envelope=transaction,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE
        )

        fee_bump_tx.sign(os.environ["STELLAR_PRIVATE_KEY"])
        response = server.submit_transaction(fee_bump_tx)
        
    return True, f"https://stellar.expert/explorer/testnet/tx/{response['id']}" # Another thing to change


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

def createClaimableBalance(private_key: str, destination: str, amount: str, asset_name=None, asset_issuer=None):
    """
    Create a Claimable Balance for a user
    """
    user_keypair = None
    try:
        user_keypair = Keypair.from_secret(private_key)
    except exceptions.Ed25519SecretSeedInvalidError:
        return False, "Private key is invalid"


    user_pub_key = user_keypair.public_key
    base_fee = server.fetch_base_fee()*3
    account = server.load_account(user_pub_key)

    claimant = Claimant(destination=destination)

    asset = Asset.native()
    if asset_name is not None and asset_issuer is not None:
        try:
            print(asset_name)
            asset = Asset(asset_name, asset_issuer)
        except exceptions.AssetIssuerInvalidError:
            return False, "The Issuer of the Asset is invalid"
        except exceptions.AssetCodeInvalidError:
            return False, "Asset Code is invalid"

    print(asset)
    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=base_fee,

        ).append_create_claimable_balance_op(
            asset=asset,
            amount=amount,
            claimants=[claimant],
            source=user_pub_key
        )
        .build()
    )
    transaction.sign(private_key)
    response = server.submit_transaction(transaction)

    try:
        response = server.submit_transaction(transaction)
        print(response)
        return True, f"https://stellar.expert/explorer/testnet/tx/{response['id']}"
    except:
        return False

def verifyItExists(asset :str, available_assets: list) -> bool:
	"""
	Check if in the balances of the account an asset like that alredy exists to establish a trustline
	"""
	for elem in available_assets:
		if elem["sponsor"] == asset:
			return True
	return False