from datetime import datetime
import json,smtplib,ssl
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetTransferTxn, SuggestedParams
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class planetSender:
    def __init__(self):
        self.error = [""]
        self.exception = False
        self.walletNames = []
        self.balanceBefores = []
        self.targetInfo = []
        self.targetInfos = []

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
            for i in range(len(datas["wallets"])):
                print(i)
                publicKey = datas["wallets"][i]["passphrase"]
                privateKey = mnemonic.to_private_key(publicKey)
                senderAddress = datas["wallets"][i]["address"] 
                algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
                algod_token = "pdWVhMhgb33g5LiWpg25rarqbAynJDRg7FhiIbWS"
                headers = {
                    "X-API-Key": algod_token,
                }
                algod_client = algod.AlgodClient(algod_token, algod_address,headers)

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
                    print(account_info)
                    balanceBefore = account_info['assets'][0]['amount']
                    print(balanceBefore)
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
                    ptx = algod_client.pending_transaction_info(txid)
                    asset_id = ptx['txn']['txn']["xaid"]
                    self.print_created_asset(algod_client, senderAddress, asset_id)
                    self.print_asset_holding(algod_client, senderAddress, asset_id)                    
                    self.targetInfo.append(datas["wallets"][i]["targetAddresses"][j]["targetAddress"])
                    self.targetInfo.append(int(amount)/1000000)
                self.walletNames.append(datas["wallets"][i]["walletName"])       
                self.balanceBefores.append(balanceBefore)
                self.targetInfos.append(self.targetInfo)
                self.targetInfo = []
                self.emailSender("")  
            return
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
            if(content == ""):
                print('Success Email Sent')
                message["Subject"] = "Succes Planet Transaction " +datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for iter in range(len(self.walletNames)):
                    row = "<p><b> Wallet "+ self.walletNames[iter]  +"</b> had <b>"+ str(self.balanceBefores[iter]/1000000) +"</b> Planets.</p>"
                    for insiter in range(len(self.targetInfos[iter])):
                        if (insiter % 2 == 0):
                            row_transaction = "<p><b>"+ str(self.targetInfos[iter][insiter+1]) +"</b> planets sent to "+ self.targetInfos[iter][insiter]  +"</p>"                    
                    row_ending = "<p>***********************************************************************************************************************<br><br></p>"
                html = "<html><body style='font-size: 16px;'>"+ row + row_transaction + row_ending +"</body></html>"              
                htmlMessage = MIMEText(html,"html")
            else:
                print('Error email Sent')
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
        result = planetSender().distributor(datas)
              
    config.close()
