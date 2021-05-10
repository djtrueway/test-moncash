from django.shortcuts import render
import moncashify
import moncash 

# Create your views here.

def moncash_api(request):
    client_id = "c4d4d73a2a00a4b816d76efb56d2304c"
    secret_key = "ZTRAhfI0m8cZgbwMj5CLpIL0FGwxUfR8t7xZBWe1LM_uhusbaeC6wx1M8OcMwj9W"

    order_id = #increment_invoice_number()
    amount = 100 # HTG

    moncash = moncashify.API(client_id, secret_key, True)

    payment = moncash.payment(order_id, amount)
    print(payment)
    # Payment object - Order ID: SH023, Amount: 1500

    url = payment.redirect_url
    print(url)
    
    return Response({
        'message': 'OK',
        'url': url
    })
    
def moncash_api_amount(request):
    client_id = "c4d4d73a2a00a4b816d76efb56d2304c"
    secret_key = "ZTRAhfI0m8cZgbwMj5CLpIL0FGwxUfR8t7xZBWe1LM_uhusbaeC6wx1M8OcMwj9W"

    order_id = #increment_invoice_number()
    amount = request.data.get('amount') 
    if amount != '' and amount != None:
        moncash = moncashify.API(client_id, secret_key, True)

        payment = moncash.payment(order_id, amount)
        print(payment)
        # Payment object - Order ID: SH023, Amount: 1500

        url = payment.redirect_url
        print(url)
        
        return Response({
            'message': 'OK',
            'url': url
        })
    else:
        return Response({
            'message': 'please give the amount ',
        }, status=status.HTTP_400_BAD_REQUEST)



def moncash_checkout_session(request):
    if request.method == 'GET':

        gateway = moncash.Moncash(
            client_id = "c4d4d73a2a00a4b816d76efb56d2304c",
            client_secret = "ZTRAhfI0m8cZgbwMj5CLpIL0FGwxUfR8t7xZBWe1LM_uhusbaeC6wx1M8OcMwj9W",
            environment=moncash.environment.Sandbox
        )

        try:
            response = gateway.payment.get_by_ref(reference="SAJES-2021-02-19-18-02-07-239")
        except moncash.exceptions.NotFoundError:
            response = None
            print("We didnt found this transaction... It is not valid")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except moncash.exceptions.MoncashError:
            response = None
            print("Unexpected error...")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(response, status=status.HTTP_201_CREATED)

    elif request.method == 'POST':

        data = request.data.get('data')

        order = increment_invoice_number()
        if data != None and data != '':

            gateway = moncash.Moncash(
            client_id = "c4d4d73a2a00a4b816d76efb56d2304c",
            client_secret = "ZTRAhfI0m8cZgbwMj5CLpIL0FGwxUfR8t7xZBWe1LM_uhusbaeC6wx1M8OcMwj9W",
            environment=moncash.environment.Sandbox
            )

            try:
                response = gateway.payment.get_by_ref(reference=order)
            except moncash.exceptions.NotFoundError:
                response = None
                print("We didnt found this transaction... It is not valid")
                return Response(status=status.HTTP_404_NOT_FOUND)
            except moncash.exceptions.MoncashError:
                response = None
                print("Unexpected error...")
                return Response(status=status.HTTP_404_NOT_FOUND)

            # add transaction in database
            imei = request.data.get('imei')
            email = request.data.get('email')
            #number = request.data.get('number')
            #price = request.data.get('price')
            #model = request.data.get('model')
            tool = data.tool
            #idpay = request.data.get('idpay')

            # create new invoice for each order
            if imei == None and email == None or imei  == '' and email == None : return Response("give email and imei number")
            new_invoice =  Invoice()
            new_invoice.save()
            user = User.objects.get(pk=request.user.pk)

            #prepare data to supliers 
            payload = {
                'serviceid': tool.order,
                'key': '6D508-18737-187S2-1D8HV-E699F-6D508',
                'imei': imei
            }

            # send data to supliers 
            reponse = requests.get('https://api.imeicheck.com/api/v1/services/order/create', params=payload)
            
            if reponse.status_code == 200:
                res = reponse.json()
                

                
                
                historydb = Historie(invoice=new_invoice, email=email, price=reponse.cost,
                                    tool=data.tool, idpay=reponse['transaction_id'], 
                                    code=res['result'], number=reponse['payer'],
                                    user=user, done=True, check=True)
                historydb.save()
                if historydb :
            
                    msg = "Merci d'avoir placé une commande sur SajesUnlock"
                    email_from = settings.EMAIL_HOST_USER
                    email_sender = [email,'support@sajesunlock.com']
                    
                    send_mail('YOUR ORDER STATUS IS : Complete.',
                    msg, email_from, email_sender,
                    fail_silently=True, html_message=data['result'])
            
                    return Response({
                        "message": "OK",
                        "gsma_db": res['result']
                        }, 
                        status=status.HTTP_201_CREATED)

            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response("should give order id ")  
