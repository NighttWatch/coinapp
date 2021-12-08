from datetime import datetime
import json,time,smtplib,ssl
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetTransferTxn
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from pretty_html_table import build_table

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
                    algod_address = "http://3.232.109.91:4001"
                    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    algod_client = algod.AlgodClient(algod_token, algod_address)

                    # CREATE ASSET
                    # Get network params for transactions before every transaction.
                    params = algod_client.suggested_params()
                    # comment these two lines if you want to use suggested params
                    params.fee = 1000
                    params.flat_fee = True
                    account_info = algod_client.account_info(senderAddress)
                    for j in range(len(datas["wallets"][i]["targetAddresses"])):
                        print('target wallet:',j)

                        receiver = datas["wallets"][i]["targetAddresses"][j]["targetAddress"]
                        balanceBefore = account_info['assets'][0]['amount']
                        amount = (int(datas["wallets"][i]["targetAddresses"][j]["percentage"])/100) * int(account_info['assets'][0]['amount'])
                        amount = str(amount).split(".")[0]
                        note = "stefanscriptv1".encode()
                        unsigned_txn = AssetTransferTxn(sender=senderAddress, sp=params,index=27165954,receiver=receiver,amt=int(amount),note=note)

                        #sign transaction
                        signed_txn = unsigned_txn.sign(privateKey)

                        #submit transaction
                        txid = algod_client.send_transaction(signed_txn)
                        print("Signed transaction with txID: {}".format(txid))

                        try:
                            # Wait for the transaction to be confirmed
                            self.wait_for_confirmation(algod_client,txid) 
                        except Exception as err:
                            print('Network Confirmation Error')
                            print(err)
                            self.error="Network Confirmation Error"
                            self.emailSender(self.error)
                            return
                        try:
                            # Pull account info for the creator
                            # account_info = algod_client.account_info(accounts[1]['pk'])
                            # get asset_id from tx
                            # Get the new asset's information from the creator account
                            ptx = algod_client.pending_transaction_info(txid)
                            print(ptx['txn']['txn']["xaid"])
                            asset_id = ptx['txn']['txn']["xaid"]
                            self.print_created_asset(algod_client, senderAddress, asset_id)
                            self.print_asset_holding(algod_client, senderAddress, asset_id)
                            self.targetInfo = []
                            self.targetInfo.append(datas["wallets"][i]["targetAddresses"][j]["targetAddress"])
                            self.targetInfo.append(int(amount)/100000)
                            time.sleep(1)
                        except Exception as e:
                            print('Sending Module Error')
                            print(e)
                            self.error=e
                            self.emailSender(self.error)
                            return
                self.walletNames.append(datas["wallets"][i]["walletName"])       
                self.balanceBefores.append(balanceBefore)
                self.targetInfos.append(self.targetInfo)
        except Exception as err:
            print('Sender Script')
            print(err)
            self.error[0] = err # sender send error
            self.emailSender(self.error)
            return


    def print_created_asset(self,algodclient, account, assetid):    
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
    def print_asset_holding(self,algodclient, account, assetid):
        
        # note: if you have an indexer instance available it is easier to just use this
        # response = myindexer.accounts(asset_id = assetid)
        # then loop thru the accounts returned and match the account you are looking for
        account_info = algodclient.account_info(account)
        print(account_info)

    def wait_for_confirmation(self,client, txid):
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

    def emailSender(self,content):
        sender_email = "emailsenderplanet@gmail.com"
        receiver_email = datas["email"]["receiver"]
        password = "T12345678."
        try:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            if(content[0] == ""):
                message["Subject"] = "Succes Planet Transaction " +datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tableDict = {'Wallet Name':self.walletNames, 'Balance Before':self.balanceBefores, 'Sending Information': self.targetInfos}
                data = pd.DataFrame(tableDict)
                htmlMessage = MIMEText(build_table(data,"grey_light"), "html")
            else:
                message["Subject"] = "Planet Transaction Error " +datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                html = "<html><body><p> " + str(content[0]) +" </p></body></html>"              
                htmlMessage = MIMEText(html,"html")


            message.attach(htmlMessage)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
        except Exception as err:
            print('Email Error')
            print(err)
            return


if __name__=="__main__":  
    config = open('./config.json')
    datas = json.load(config)
    error = planetSender().controlPercentage(datas)
    if (error == "Clear"):
        planetSender().distributor(datas)
    planetSender().emailSender("")  
    config.close()
