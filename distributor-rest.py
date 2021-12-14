import algosdk
from algosdk.future.transaction import AssetTransferTxn, SuggestedParams,SignedTransaction
from algosdk import mnemonic
import requests,json,time

class planetSender:
    def __init__(self):
        self.error = [""]
        self.exception = False
        self.targetInfos = []
        self.walletNames = []
        self.balanceBefores = []
        self.targetInfo = []

    def controlPercentage(self,datas):
        try:
            for i in range(1000):
                if (len(datas["wallets"]) == i):
                    break
                else:                
                    totalPer = 0
                    for j in range(len(datas["wallets"][i]["targetAddresses"])):
                        totalPer += datas["wallets"][i]["targetAddresses"][j]["percentage"]
                    if (totalPer != 100):
                        raise PermissionError()
        except PermissionError:
            self.error = "unacceptable percentage for wallet: {}".format(datas["wallets"][i]["walletName"])
            print("unacceptable percentage for wallet:", datas["wallets"][i]["walletName"])
            self.exception = True
        finally:
            if self.exception == False:
                return "Clear"
            else:
                print('Control Percentage Error')
                self.emailSender(self.error)
                return self.error # sender send error

    def distributor(self,datas):
        try:
            for i in range(1000):
                print(i)
                if (len(datas["wallets"]) == i):
                    break
                else:
                    publicKey = datas["wallets"][i]["passphrase"]
                    privateKey = mnemonic.to_private_key(publicKey)
                    senderAddress = datas["wallets"][i]["address"] 

                    # Get network params for transactions before every transaction.
                    params = requests.get('https://algoexplorerapi.io/v2/transactions/params')
                    params = params.json()
                    account_info = requests.get(f"https://algoexplorerapi.io/v2/accounts/{senderAddress}")
                    account_info = account_info.json()
                    for j in range(len(datas["wallets"][i]["targetAddresses"])):
                        print('target wallet:',j)

                        receiver = datas["wallets"][i]["targetAddresses"][j]["targetAddress"]
                        print(account_info)
                        balanceBefore = account_info['assets'][0]['amount']
                        print(balanceBefore)
                        amount = (int(datas["wallets"][i]["targetAddresses"][j]["percentage"])/100) * int(account_info['assets'][0]['amount'])
                        amount = str(amount).split(".")[0]
                        note = "stefanscriptv1".encode()
                        sp = SuggestedParams(fee=1000,first=0,last=0,gh=params['genesis-hash'],gen=params['genesis-id'],flat_fee=True)
                        unsigned_txn = AssetTransferTxn(sender=senderAddress, sp=sp,index=27165954,receiver=receiver,amt=int(amount),note=note)
                        #sign transaction
                        signed_txn = unsigned_txn.sign(privateKey)
                        print(signed_txn)
                        #submit transaction
                        header = {
                            'Content-Type': 'application/x-binary'
                        }
                        txid = requests.post('https://algoexplorerapi.io/v2/transactions',data=signed_txn,headers=header)
                        print("Signed transaction with txID: {}".format(txid.json()))
                        """
                        try:
                            # Wait for the transaction to be confirmed
                            self.wait_for_confirmation(algod_client,txid) 
                        except Exception as err:
                            print('Network Confirmation Error')
                            print(err)
                            self.error="Network Confirmation Error"
                            #self.emailSender(self.error)
                            return
                        try:
                            # Pull account info for the creator
                            # account_info = algod_client.account_info(accounts[1]['pk'])
                            # get asset_id from tx
                            # Get the new asset's information from the creator account
                            ptx = algod_client.pending_transaction_info(txid)
                            print(ptx['txn']['txn']["xaid"])
                            asset_id = ptx['txn']['txn']["xaid"]
                            self.targetInfo = []
                            self.targetInfo.append(datas["wallets"][i]["targetAddresses"][j]["targetAddress"])
                            self.targetInfo.append(int(amount)/100000)
                            time.sleep(1)
                        except Exception as e:
                            print('Sending Module Error')
                            print(e)
                            self.error=e
                            #self.emailSender(self.error)
                            return
                            """
                self.walletNames.append(datas["wallets"][i]["walletName"])       
                self.balanceBefores.append(balanceBefore)
                self.targetInfos.append(self.targetInfo)
        except Exception as err:
            print('Sender Script')
            print(err)
            self.error[0] = err # sender send error
            #self.emailSender(self.error)
            return "Success"


if __name__=="__main__":  
    config = open('./config.json')
    datas = json.load(config)
    error = planetSender().controlPercentage(datas)
    if (error == "Clear"):
        planetSender().distributor(datas)
    elif (error == "Success"):
        pass
        #planetSender().emailSender("")  
    config.close()