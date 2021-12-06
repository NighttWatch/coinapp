import json,sys
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn

def account(address,passphrase):
    print("My address: {}".format(address))
    print("My private key: {}".format(mnemonic.to_private_key(passphrase)))
    private_key = mnemonic.to_private_key(passphrase)
    #print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
    return address,private_key


def first_transaction_example(private_key, my_address):
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # CREATE ASSET
    # Get network params for transactions before every transaction.
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    params.fee = 1000
    params.flat_fee = True

    #params.xaid = 27165954
    receiver = "H67BCVJAV3W2KW65MCPMJKGBRXDU5BBS57P25SM2CZSYNA5LYHS7XD635Y"
    note = "stefan script v1".encode()
    unsigned_txn = AssetTransferTxn(sender=my_address, sp=params,index=27165954,receiver=receiver,amt=100000)

    #sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    #submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    try:
        # Wait for the transaction to be confirmed
        wait_for_confirmation(algod_client,txid) 
    except Exception as err:
        print(err)
        return
    try:
        # Pull account info for the creator
        # account_info = algod_client.account_info(accounts[1]['pk'])
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        print_created_asset(algod_client, my_address, asset_id)
        print_asset_holding(algod_client, my_address, asset_id)
    except Exception as e:
        print(e)

    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('assets')[0].get('amount')))

    

   

def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo
#   Utility function used to print created asset for account and assetid
def print_created_asset(algodclient, account, assetid):    
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = algodclient.account_info(account)
    idx = 0;
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1       
        if (scrutinized_asset['index'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break
#   Utility function used to print asset holding for account and assetid
def print_asset_holding(algodclient, account, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break

my_address,private_key = account("H67BCVJAV3W2KW65MCPMJKGBRXDU5BBS57P25SM2CZSYNA5LYHS7XD635Y","winter bind pattern taste expect blur vague bar latin hotel rug trumpet burden horse submit name ugly culture deny clip awesome edit spray above rely")

first_transaction_example(private_key,my_address)