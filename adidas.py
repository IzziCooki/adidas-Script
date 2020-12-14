import requests
import json
import threading
import time
from bs4 import BeautifulSoup



def URLGen(model, size):
    BaseSize = 580
    # Base Size is for Shoe Size 6.5
    ShoeSize = size - 6.5
    ShoeSize = ShoeSize * 20
    RawSize = ShoeSize + BaseSize
    ShoeSizeCode = int(RawSize)
    URL = 'http://www.adidas.com/us/' + str(model) + '.html?forceSelSize=' + str(model) + '_' + str(ShoeSizeCode)
    return ShoeSizeCode, URL


def CheckStock(productId, delay):
    InStock = False  # Don't change
    user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
    headers = {'User-Agent': user_agent}
    while InStock == False:
        # Adidas requests link to check Stock
        availabilityLink = f'https://www.adidas.com/api/products/{productId}/availability?sitePath=us'
        RawHTML = requests.get(availabilityLink, headers=headers)
        jsons = RawHTML.json()
        # List of all shoes and if they are availble
        # Stock prints IN_STOCK or Not_IN_STOCKv
        stock = jsons['availability_status']

        if stock == 'IN_STOCK':
            print('In Stock')
            InStock == True
            checkout()
        else:
            print("Not in Stock")
            InStock == False
        time.sleep(delay)


class checkout():
    def __init__(self):
        self.email = input('Enter Email: ')
        self.firstName = input('Enter firstName: ')
        self.lastName = input('Enter lastName: ')
        self.address = input('Enter address: ')
        self.city = input('Enter city: ')
        self.zipcode = input('Enter zipcode: ')
        self.stateCode = input('Enter stateCode: ')
        self.phoneNum = input('Enter phoneNum: ')
        self.cardNum = input('Enter cardNum: ')
        self.paymentBrand = input('Enter paymentBrand: ')
        self.cardName = input('Enter cardName: ')
        self.CCV = input('Enter CCV: ')
        self.expMonth = input('Enter expMonth Ex(07): ')
        self.expYear = input('Enter expYear Ex(2025): ')
        self.productId = input('Enter productId: ')
        self.size = input("Enter Size:")
        self.delay = input("Enter Delay (in seconds): ")
        self.delay = float(self.delay)
        self.ShoeSizeCode = '650'  # Don't Change
        self.s = requests.Session()
        self.addToCart()



    def addToCart(self):
        headers = {
            'authority': 'www.adidas.com',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'accept': '*/*',
            'origin': 'https://www.adidas.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'https://www.adidas.com/us/{self.productId}.html',
            'accept-language': 'en-US,en;q=0.9'}

        params = (
            ('sitePath', 'us'),
        )
        data2 = '{"product_id":"EG0758","quantity":1,"product_variation_sku":"EG0758_650","productId":"EG0758_650","size":"10.5"}'
        data = {"product_id": self.productId, "quantity": 1, "product_variation_sku": f"{self.productId}_{self.ShoeSizeCode}",
                "productId": f"{self.productId}_{self.ShoeSizeCode}", "size": self.size}

        # Add product to card
        atc = self.s.post('https://www.adidas.com/api/baskets/-/items', headers=headers, params=params, json=data,
                     timeout=10)
        # Creats Auth token to be used later
        auth = atc.headers['Authorization']
        # Creates Bsketid that will be used throught the whole request
        basketId = json.loads(atc.text)
        basketId = str(basketId['basketId'])
        print(atc.text)
        self.shipping(auth, basketId)

    def shipping(self, auth, basketId):
        headers = {
            'authority': 'www.adidas.com',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'accept': '*/*',
            'origin': 'https://www.adidas.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'https://www.adidas.com/us/{self.productId}.html',
            'accept-language': 'en-US,en;q=0.9'}

        # Payload for shipping details
        datas = {"customer": {"email": self.email, "receiveSmsUpdates": 'false'},
                 "shippingAddress": {"address1": self.address, "city": self.city, "country": "US", "firstName": self.firstName,
                                     "lastName": self.lastName, "zipcode": self.zipcode, "stateCode": self.stateCode,
                                     "emailAddress": self.email, "phoneNumber": self.phoneNum},
                 "billingAddress": {"address1": self.address, "city": self.city, "country": "US", "firstName": self.firstName,
                                    "lastName": self.lastName, "zipcode": self.zipcode, "stateCode": self.stateCode,
                                    "emailAddress": self.email, "phoneNumber": self.phoneNum}}

        shipping = self.s.get(f'https://www.adidas.com/api/checkout/baskets/{basketId}/payment_methods?sitePath=us',
                         headers=headers, json=datas, timeout=10)
        # Get checkoutId
        checkoutId = json.loads(shipping.text)
        checkoutId = str(checkoutId['checkoutId'])
        self.payment(auth, checkoutId, basketId)

    def payment(self, auth, checkoutId, basketId):
        headers3 = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://www.adidas.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'iframe',
            'Referer': 'https://www.adidas.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        # Payment Info payload
        data3 = {
            'card.number': self.cardNum,
            'paymentBrand': self.paymentBrand,
            'card.holder': self.cardName,
            'shopperResultUrl': f'https://www.adidas.com/us/payment/callback/CREDIT_CARD/{basketId}/aci',
            'forceUtf8': '&#9760;',
            'shopOrigin': 'https://www.adidas.com',
            'card.cvv': self.CCV,
            'card.expiryMonth': self.expMonth,
            'card.expiryYear': self.expYear,

        }
        # Updates cart with payment info added
        response1 = self.s.post(f'https://oppwa.com/v1/checkouts/{checkoutId}', headers=headers3, data=data3, timeout=10)
        print(response1.text)
        self.confirmCheckout(auth, checkoutId, basketId)

    def confirmCheckout(self, auth, checkoutId, basketId):
        # Final payload to confirm Submit Order
        fc = {"basketId": basketId, "paymentInstrument": {"paymentMethodId": "CREDIT_CARD"}}

        headers = {
            'authority': 'www.affirm.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'referer': 'https://www.adidas.com/',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'DUMMY_COOKIE=DUMMY_VALUE',
            'content-type': 'application/json',
            'origin': 'https://www.adidas.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://www.adidas.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'iframe',
            'Referer': 'https://www.adidas.com/',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-User': '?1',
            'x-requested-with': 'XMLHttpRequest',
            'X-HTTP-Method-Override': 'FORM',
            'Content-Length': '0',
            'checkout-authorization': auth,
        }

        params = (
            ('resourcePath', f'/v1/checkouts/{checkoutId}'),
        )

        finalCheckout = self.s.post(f'https://www.adidas.com/us/payment/callback/CREDIT_CARD/{basketId}/aci',
                               headers=headers, params=params, json=fc, timeout=10)
        if finalCheckout.status_code == 200:
            print('Processing Order')
            self.s.close()
            # Ends loop
            exit()
        else:
            print("Order Failed Retying")
            checkout()

CheckStock('FW7033', 0.4)  #ProductId and delay in seconds
