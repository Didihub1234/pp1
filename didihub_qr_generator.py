import requests
import json
import time
import webbrowser
import os
from urllib.parse import urlparse

# TOKEN dan CHAT_ID Telegram
TELEGRAM_TOKEN = '7805960444:AAEb3UUNT3DZUfds6G2trRLv8UrJtLZfyyc'
CHAT_ID = '-1002500559635'

# Data login didihub
LOGIN_URL = 'https://www.didihub.com/api/main/user/email/login'
PAY_CHANNEL_URL = 'https://www.didihub.com/api/main/pay/channel'
PAY_POST_URL = 'https://www.didihub.com/api/main/pay/67'  # Channel QRIS id=67

email = "gunawan.skr@gmail.com"
password = "Gunawan2347"
browserVisitorId = "05467f96e147f52215497fe02e9d24e0"
programVisitorId = "8650KmEtzpHDEjWb"

# Data pembayaran
pay_amount = "199000"
pay_phone = "822328947322"
pay_name = "ASEp"

def send_telegram_message(token, chat_id, message):
    """Fungsi untuk mengirim pesan ke Telegram dengan penanganan error yang lebih baik"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        print(f"Status respons Telegram: {resp.status_code}")
        print(f"Isi respons: {resp.text}")
        
        if resp.status_code == 200:
            return True
        else:
            print(f"Error mengirim pesan ke Telegram: {resp.text}")
            return False
    except Exception as e:
        print(f"Exception saat mengirim pesan ke Telegram: {str(e)}")
        return False

def validate_url(url):
    """Validasi apakah URL valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def open_qr_url(url):
    """Membuka URL QR code di browser default"""
    try:
        if validate_url(url):
            print(f"Membuka URL QR code: {url}")
            webbrowser.open(url)
            return True
        else:
            print(f"URL tidak valid: {url}")
            return False
    except Exception as e:
        print(f"Error membuka URL: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("DIDIHUB QR CODE GENERATOR")
    print("=" * 50)
    print("Memulai proses...")
    
    # Login ke didihub
    login_payload = {
        "email": email,
        "password": password,
        "browserVisitorId": browserVisitorId,
        "programVisitorId": programVisitorId
    }
    login_headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.didihub.com",
        "Referer": "https://www.didihub.com/"
    }

    try:
        print("\n[1/4] Mencoba login ke didihub...")
        login_resp = requests.post(LOGIN_URL, json=login_payload, headers=login_headers, timeout=30)
        print(f"Status login: {login_resp.status_code}")
        
        if login_resp.status_code != 200:
            print("❌ Login gagal:", login_resp.text)
            return False
       
        login_data = login_resp.json()
        token = login_data.get("token")
        if not token:
            print("❌ Token tidak ditemukan dalam respons:", login_data)
            return False
       
        print("✅ Login sukses, token diterima.")
       
        # Request channel pembayaran
        headers_auth = {
            "Authorization": f"Bearer {token}",
            "User_token": token
        }
        
        print("\n[2/4] Mengambil informasi channel pembayaran...")
        channel_resp = requests.get(PAY_CHANNEL_URL, headers=headers_auth, timeout=30)
        if channel_resp.status_code != 200:
            print("❌ Gagal ambil channel pembayaran:", channel_resp.text)
            return False
       
        print("✅ Channel pembayaran berhasil diambil.")
       
        # Request pembayaran via channel QRIS id=67
        pay_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User_token": token,
            "Origin": "https://www.didihub.com",
            "Referer": "https://www.didihub.com/"
        }
       
        pay_payload = {
            "amount": pay_amount,
            "phone": pay_phone,
            "name": pay_name
        }
       
        print("\n[3/4] Memproses pembayaran...")
        pay_resp = requests.post(PAY_POST_URL, json=pay_payload, headers=pay_headers, timeout=30)
        if pay_resp.status_code != 200:
            print("❌ Gagal request pembayaran:", pay_resp.text)
            return False
       
        pay_result = pay_resp.json()
        print("✅ Pembayaran berhasil diproses.")
        print("Respons:", json.dumps(pay_result, indent=2))
       
        # Cari URL QR code dari berbagai kemungkinan field
        qr_code_url = None
        possible_fields = ['qrCodeUrl', 'qr_code', 'qr', 'qrCode', 'qrUrl', 'url', 'qr_url', 'code_url']
        
        print("\n[4/4] Mencari URL QR Code...")
        for field in possible_fields:
            if field in pay_result:
                qr_code_url = pay_result[field]
                print(f"✅ URL QR Code ditemukan di field '{field}'")
                break
                
        # Jika tidak ditemukan di level atas, cari di nested objects
        if not qr_code_url:
            for key, value in pay_result.items():
                if isinstance(value, dict):
                    for field in possible_fields:
                        if field in value:
                            qr_code_url = value[field]
                            print(f"✅ URL QR Code ditemukan di nested field '{key}.{field}'")
                            break
                    if qr_code_url:
                        break
       
        # Proses URL QR Code
        if qr_code_url:
            print(f"\n🎯 URL QR Code: {qr_code_url}")
            
            # Buka URL QR code otomatis
            print("\n🌐 Membuka QR code di browser...")
            if open_qr_url(qr_code_url):
                print("✅ QR code berhasil dibuka di browser!")
            else:
                print("❌ Gagal membuka QR code di browser")
            
            # Kirim ke Telegram
            print("\n📱 Mengirim URL ke Telegram...")
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                print(f"Percobaan ke-{attempt} mengirim pesan ke Telegram...")
                if send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, qr_code_url):
                    print("✅ URL berhasil dikirim ke Telegram.")
                    break
                else:
                    print(f"❌ Gagal mengirim URL ke Telegram pada percobaan ke-{attempt}.")
                    if attempt < max_attempts:
                        print("Mencoba lagi dalam 5 detik...")
                        time.sleep(5)
            else:
                print(f"❌ Gagal mengirim URL ke Telegram setelah {max_attempts} percobaan.")
                
            return True
        else:
            print("❌ URL QR Code tidak ditemukan dalam response.")
            print("Isi lengkap response:", json.dumps(pay_result, indent=2))
            
            # Kirim seluruh response ke Telegram untuk debugging
            debug_message = f"QR URL tidak ditemukan. Response: {json.dumps(pay_result, indent=2)}"
            send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, debug_message)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error koneksi: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error tidak terduga: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n" + "="*50)
            print("🎉 PROSES SELESAI DENGAN SUKSES!")
            print("QR Code telah dibuka di browser Anda.")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("❌ PROSES GAGAL!")
            print("Silakan periksa log error di atas.")
            print("="*50)
    except KeyboardInterrupt:
        print("\n\n⚠️ Proses dibatalkan oleh user.")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
    
    input("\nTekan Enter untuk keluar...")
