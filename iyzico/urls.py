from django.urls import path

from iyzico.views import (payment_with_form,
                          payment_with_api,
                          payment_with_api_with_saved_payment_card,
                          payment_with_threeds,
                          success,
                          threeds_success,
                          create_card,
                          create_second_card,
                          retrieve_cards,
                          retrieve_bin,
                          delete_payment_card
                          )

urlpatterns = [
    path('create-card', create_card, name="create-card"),
    path('create-second-card', create_second_card, name="create-second-card"),
    path('retrieve-cards', retrieve_cards, name="retrieve-cards"),
    path('retrieve-bin', retrieve_bin, name="retrieve-bin"),
    path('delete-card', delete_payment_card, name="delete-card"),
    path('payment', payment_with_form, name="payment"),
    path('payment-with-api', payment_with_api, name="payment-with-api"),
    path('payment-with-threeds', payment_with_threeds, name="payment-with-threeds"),
    path('payment-with-api-with-saved-card', payment_with_api_with_saved_payment_card,
         name="payment-with-api-with-saved-payment-card"),
    path('threeds-success', threeds_success, name="threeds-success"),
    path('success', success, name="success")
]
