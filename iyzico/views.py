import base64
import json
import iyzipay

from django.conf import settings
from django.shortcuts import render, reverse, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from iyzico.models import UserPaymentCard

"""
    Iyzico üzerinde form üzerinden kartımı sakla denildiği zaman
    kart bilgisine ait olan -> cardToken,cardUserKey
    bilgiside gelmektedir böylece bu değerler tutularak kart bilgilerinin sorgusu yapılabilir.
"""

"""
Pazar yeri isek ve submerchant olmadan satış yapmak için
paymentGroup -> Listing olabilir. Bu iyzico dökümanında mevcut değil bunu dikkate al.
Yoksa herbir satışta senden subMerchantKey isteyecektir.
"""

# Create your views here.

def create_card(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    card_information = {
        'cardAlias': 'card alias',
        'cardHolderName': 'John Doe',
        'cardNumber': '5528790000000008',
        'expireMonth': '12',
        'expireYear': '2030'
    }

    data = {
        'locale': 'tr',
        'conversationId': '123',
        'email': "ozanteomandayanan@gmail.com",
        'externalId': "1",
        'card': card_information
    }

    card = iyzipay.Card()
    card_response = card.create(data, options)
    response = json.loads(card_response.read().decode('utf-8'))

    print(response)
    if response['status'] == "success":
        UserPaymentCard.objects.create(
            user_id=1,
            card_user_key=response["cardUserKey"],
            card_token=response["cardToken"]
        )

    return JsonResponse(response)


def create_second_card(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': 'tr',
        'conversationId': "1995",
        'cardUserKey': "PQ9p7RGMi5sfYYa/49XT+lmZWJo=",
        'card': {
            'cardAlias': 'card alias',
            'cardHolderName': 'John Doe',
            'cardNumber': '5528790000000008',
            'expireMonth': '12',
            'expireYear': '2030'
        }
    }

    card = iyzipay.Card()
    card_response = card.create(data, options)
    response = json.loads(card_response.read().decode('utf-8'))

    print(response)
    if response['status'] == "success":
        UserPaymentCard.objects.create(
            user_id=1,
            card_user_key=response["cardUserKey"],
            card_token=response["cardToken"]
        )

    return JsonResponse(data=response)


def retrieve_cards(request):
    card_user_key = "PQ9p7RGMi5sfYYa/49XT+lmZWJo="

    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'cardUserKey': card_user_key,
        'locale': 'tr',
        'conversationId': "1995"
    }

    card_list = iyzipay.CardList()
    card_list_response = card_list.retrieve(data, options)

    response = json.loads(card_list_response.read().decode('utf-8'))
    print(response)

    return JsonResponse(data=response)


def retrieve_bin(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': "tr",
        'conversationId': "1995",
        'binNumber': '552879'
    }

    bin_number = iyzipay.BinNumber().retrieve(data, options)

    response = json.loads(bin_number.read().decode('utf-8'))
    return JsonResponse(data=response)


def delete_payment_card(request):
    # this card will be deleted on iyzico
    payment_card = UserPaymentCard.objects.first()

    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': "tr",
        'cardToken': payment_card.card_token,
        'cardUserKey': payment_card.card_user_key,
        'conversationId': "1995"
    }

    card = iyzipay.Card()
    card_response = card.delete(data, options)
    response = json.loads(card_response.read().decode('utf-8'))

    return JsonResponse(data=response)


def payment_with_form(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    buyer = {
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '25'
        }
    ]

    data = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '25',
        'paidPrice': '25',
        'currency': 'TRY',
        'installment': '1',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": f"http://localhost:8000{reverse('success')}",
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,

    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(data, options)
    result = checkout_form_initialize.read().decode('utf-8')
    print(result)
    result = json.loads(result)
    form = f"{result['checkoutFormContent']}"

    return render(request, 'payment_form_screen.html', context={'form': form})


def payment_with_api(request):
    """
    3D security olmadan  iyzico endpointi üzerinden api kullanılarak
     satın alınma işleminde, callback url'e gerek duyulmuyor.

    Eğer registerCard : 1 olarak işaretlenirse kartın kaydelieceğini ve dönüşte kayıtl
    bilgilerini dönderecektir.
    :param request:
    :return:
    """
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    payment_card = {
        'cardHolderName': 'John Doe',
        'cardNumber': '5528790000000008',
        'expireMonth': '12',
        'expireYear': '2030',
        'cvc': '123',
        'registerCard': '0'
    }

    buyer = {
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '10'
        }
    ]

    data = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '10',
        'paidPrice': '12',
        'currency': 'TRY',
        'installment': '1',
        'basketId': 'B67832',
        'paymentChannel': 'WEB',
        'paymentGroup': 'PRODUCT',
        'paymentCard': payment_card,
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items
    }

    payment = iyzipay.Payment().create(data, options)

    response = json.loads(payment.read().decode('utf-8'))
    return JsonResponse(data=response)


def payment_with_api_with_saved_payment_card(request):
    payment_card = UserPaymentCard.objects.last()

    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    payment_card = {
        'cardUserKey': payment_card.card_user_key,
        'cardToken': payment_card.card_token
    }

    buyer = {
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '60'
        }
    ]

    data = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '60',
        'paidPrice': '60',
        'currency': 'TRY',
        'installment': '1',
        'basketId': 'B67832',
        'paymentChannel': 'WEB',
        'paymentGroup': 'PRODUCT',
        'paymentCard': payment_card,
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items
    }

    payment = iyzipay.Payment().create(data, options)

    response = json.loads(payment.read().decode('utf-8'))
    return JsonResponse(data=response)


def payment_with_threeds(request):
    payment_card = UserPaymentCard.objects.last()

    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    payment_card = {
        'cardUserKey': payment_card.card_user_key,
        'cardToken': payment_card.card_token
    }

    buyer = {
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '60'
        }
    ]

    data = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '60',
        'paidPrice': '58',
        'currency': 'TRY',
        'installment': '1',
        'basketId': 'B67832',
        'paymentChannel': 'WEB',
        'paymentGroup': 'PRODUCT',
        'paymentCard': payment_card,
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        "callbackUrl": f"http://localhost:8000{reverse('threeds-success')}",
    }

    threeds_initialize = iyzipay.ThreedsInitialize().create(data, options)
    response = json.loads(threeds_initialize.read().decode('utf-8'))

    if response["status"] == "success":
        form = base64.b64decode(response["threeDSHtmlContent"]).decode('utf-8')
        return HttpResponse(form)

    return JsonResponse(data=response)


@csrf_exempt
def threeds_success(request):
    print(request.POST)
    if request.POST.get('mdStatus') == '1':
        options = {
            'api_key': settings.IYZIPAY_API_KEY,
            'secret_key': settings.IYZIPAY_API_SECRET,
            'base_url': settings.IYZIPAY_API_BASE_URL
        }

        data = {
            'locale': 'tr',
            'paymentId': request.POST["paymentId"],
        }

        threeds_payment = iyzipay.ThreedsPayment().create(data, options)
        response = json.loads(threeds_payment.read().decode('utf-8'))
        return JsonResponse(data=response)

    return JsonResponse(data=request.POST)


@csrf_exempt
def success(request):
    print(request.POST)
    token = request.POST.get('token')

    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': 'tr',
        'token': token
    }

    checkout_form_result = iyzipay.CheckoutForm().retrieve(data, options)

    response = json.loads(checkout_form_result.read().decode('utf-8'))
    return JsonResponse(data=response)


def retrieve_payment_result(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': 'tr',
        'paymentId': '12277814',
    }

    payment = iyzipay.Payment().retrieve(data, options)
    response = json.loads(payment.read().decode('utf-8'))

    return JsonResponse(data=response)


def cancel_order(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': "tr",
        'paymentId': '12280331',
        'ip': '85.34.78.112',
    }

    cancel = iyzipay.Cancel().create(data, options)
    response = json.loads(cancel.read().decode('utf-8'))

    return JsonResponse(data=response)


def refund_order(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    data = {
        'locale': "tr",
        'paymentId': '12280324',
        'paymentTransactionId': '12985845',
        'ip': '85.34.78.112',
        'price': '60',

    }

    refund = iyzipay.Refund().create(data, options)
    response = json.loads(refund.read().decode('utf-8'))
    return JsonResponse(data=response)


def create_personel_submerchant(request):
    options = {
        'api_key': settings.IYZIPAY_API_KEY,
        'secret_key': settings.IYZIPAY_API_SECRET,
        'base_url': settings.IYZIPAY_API_BASE_URL
    }

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'subMerchantExternalId': 'B49224',
        'subMerchantType': 'PERSONAL',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'contactName': 'John',
        'contactSurname': 'Doe',
        'email': 'email@submerchantemail.com',
        'gsmNumber': '+905350000000',
        'name': 'John\'s market',
        'iban': 'TR180006200119000006672315',
        'identityNumber': '31300864726',
        'currency': 'TRY'
    }

    sub_merchant = iyzipay.SubMerchant().create(request, options)
    response = json.loads(sub_merchant.read().decode('utf-8'))
    return JsonResponse(data=response)
