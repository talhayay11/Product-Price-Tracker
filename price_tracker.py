import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# MongoDB Bağlantısı Kuruluyor
client = MongoClient('mongodb://localhost:27017/')
db = client['price_tracker']
products = db['products']
price_history = db['price_history']

# Ürün Bilgisi Ekleyen Fonksiyon (Bu fonksiyonla ürünleri veritabanına önceden ekleyebilirsiniz)
def add_product(product_id, name, url, category=None):
    product_data = {
        "_id": product_id,
        "name": name,
        "category": category,
        "url": url
    }
    products.update_one({"_id": product_id}, {"$set": product_data}, upsert=True)
    print(f"Ürün bilgisi eklendi veya güncellendi: {name}")

# Fiyat Bilgisi Ekleyen Fonksiyon
def add_price_history(product_id, price):
    price_data = {
        "product_id": product_id,
        "price": price,
        "timestamp": datetime.now().isoformat()
    }
    # Veritabanına yeni bir fiyat kaydı ekliyor
    result = price_history.insert_one(price_data)
    if result.inserted_id:
        print(f"Fiyat kaydedildi: {product_id} - {price}")
    else:
        print("Fiyat kaydedilirken bir sorun oluştu.")

# Ürün Fiyatı Çeken ve Kaydeden Fonksiyon
def fetch_and_store_price(product_id):
    # Veritabanından ürün bilgilerini al
    product = products.find_one({"_id": product_id})
    if not product:
        print("Ürün bulunamadı.")
        return

    url = product['url']
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        price_element = soup.find('span', {'class': 'prc-dsc'})  # HTML yapısına göre ayarlayın
        if price_element:
            try:
                price = float(price_element.text.strip().replace(',', '').replace(' TL', ''))
                add_price_history(product_id, price)
            except ValueError:
                print("Fiyat okunamadı.")
        else:
            print("Fiyat bilgisi bulunamadı.")
    else:
        print("Sayfa erişimi başarısız!")

# Ana Program
if __name__ == "__main__":
    # İlk kez çalıştırıyorsanız ürün bilgilerini veritabanına ekleyin
    # Örnek ürün ekleme, sadece bir kez çalıştırmanız yeterlidir.
    # add_product("12345", "Samsung Galaxy S21", "https://www.trendyol.com/samsung/galaxy-s24-256-gb-siyah-p-792775314?boutiqueId=61&merchantId=649556", "Electronics")

    # Fiyat bilgisi çekme ve saklama
    fetch_and_store_price("12345")