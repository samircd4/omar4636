import scrapy
from scrapy.crawler import CrawlerProcess
import json
from rich import print

class GetProductSpider(scrapy.Spider):
    name = "get_products"
    
    headers = {
        "cookie": "TS01c76045=011ba495a5d6efe3284da003eaf83ad37de467faa367b0b1695dd05cc7770ee7520501e4951e373ac3e94298cac0d621b3a0e00d58",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "_gid=GA1.3.1779123551.1719922839; sessionId=0.8450054639742934; _hjSession_3630004=eyJpZCI6IjMwNmEwMGI4LWE1MGUtNGU5Ni1hN2ZjLTVmZmIzMjBmYjQwOCIsImMiOjE3MTk5MjI4NDg4MjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjSessionUser_3630004=eyJpZCI6Ijc2MWIwYmEwLWIxNmMtNWMxNi04MDM0LWQyODUzMTk3ODc1NiIsImNyZWF0ZWQiOjE3MTk5MjI4NDg4MjUsImV4aXN0aW5nIjp0cnVlfQ==; TS01c76045=011ba495a544bbaf21de291a67724c90768b288bd0a859dd53e1fb116142afdc062295dc20ad16d441749b817bb02a7223fb2f94d6; site24x7rumID=64369725234124.1719925271174.1719925330603; _gat_UA-141667814-1=1; _ga_EVT41FKR71=GS1.1.1719922838.1.1.1719925432.0.0.0; _ga_MT7LWM2FM2=GS1.1.1719922838.1.1.1719925432.0.0.0; _ga=GA1.3.581871748.1719922838; _gat_gtag_UA_141667814_1=1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
    }
    
    def retry(self, querystring):
        page_number = querystring.get('page')
        p_type = querystring.get('type')
        with open('faild.txt', 'a') as f:
            f.write(f'{page_number}, {p_type}\n')
    
    def start_requests(self):
        p_type = 'MDMAGHTF'
        with open('faild.txt', 'r') as f:
            lines = f.readlines()
            
        for i in range(1001,3001):
            querystring = {"type":p_type,"page":i}
            url = f'https://www.sfda.gov.sa/GetMedicalEquipmentsSearch2.php?type={p_type}&page={i}'
            # url = "https://www.sfda.gov.sa/GetMedicalEquipmentsSearch2.php"
            yield scrapy.Request(url, headers=self.headers, meta=querystring)
    
    def parse(self, response):
        data = json.loads(response.text)['data']['ghtfTfaProductObjects']
        page_number = response.meta.get('page')
        p_type = response.meta.get('type')
        if len(data) == 0:
            print(f'No data found for page {response.meta.get("page")}')
            querystring = {"type":p_type,"page":page_number}
            return self.retry(querystring)
            
        else:
            print(f'data found for page {response.meta.get("page")}')
            
        products = []
        for d in data:
            product = {}
            product_id = d['productId']
            brand_name = d.get('brandName','')
            authorization_number = d['authorizationNumber']
            medical_device_listing_number = d.get('medicalDeviceListingNumber','')
            device_type = d.get('deviceType','')
            description = d['productDescription']
            category = d.get('productCategory','')
            classification = d['deviceClassification']
            gmdn = d['gmdn']
            manufacturer_name = d['manufacturerName']
            authorized_representative = d['authorizedRepresentative']
            expire_date = d.get('expiryDate','')
            mdi_number = d.get('manufacturerDeviceIdentifierNumber','')
            manufacturer_name = d.get('manufacturerName','')
            # model_number = d['modelNumber']
            status = d['status']
            device_accessories = d.get('deviceAccessories')
            device_accessories_trade_name = ' ,'.join([da['tradeName'] for da in device_accessories])
            try:
                device_accessories_description = ' ,'.join([da['description'] for da in device_accessories])
            except:
                device_accessories_description = ''
            device_accessories_gmdn = ', '.join([da['gmdn'] for da in device_accessories])
            
            if mdi_number is None:
                mdi_number = ''
            elif len(mdi_number) >10000:
                mdi_number = 'Too Big'
            else:
                mdi_number = mdi_number.replace('\n', ' ')
            
            # if model_number is None:
            #     model_number = ''
            # else:
            #     model_number = model_number.replace('\n', ',')
            
            product['page_number'] = response.meta.get('page')
            product['product_id'] = product_id
            product['brand_name'] = brand_name
            product['authorization_number'] = authorization_number
            product['medical_device_listing_number'] = medical_device_listing_number
            product['device_type'] = device_type
            product['description'] = description
            product['category'] = category
            product['classification'] = classification
            product['gmdn'] = gmdn
            product['manufacturer_name'] = manufacturer_name
            product['authorized_representative'] = authorized_representative
            product['expire_date'] = expire_date
            product['mdi_number'] = mdi_number
            product['manufacturer_name'] = manufacturer_name
            # product['model_number'] = model_number
            product['status'] = status
            product['product_type'] = p_type
            product['device_accessories_trade_name'] = device_accessories_trade_name
            product['device_accessories_description'] = device_accessories_description
            product['device_accessories_gmdn'] = device_accessories_gmdn
            
            print(product)
            yield product
            products.append(product)
    


process = CrawlerProcess(settings={
    'LOG_LEVEL':'WARNING',
    'FEED_FORMAT': 'csv',
    'FEED_URI': 'products.csv',
})

process.crawl(GetProductSpider)
process.start()
