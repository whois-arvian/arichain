import requests
import random
import time
import string
import names
from colorama import Fore, Style, init
from datetime import datetime
from bs4 import BeautifulSoup

init()

ANDROID_USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A346B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A236B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; moto g(30)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; CPH2211) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; V2169) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
]

class TempMailClient:
    def __init__(self, proxy_dict=None):
        self.base_url = "https://www.email-fake.com/api/v1"
        self.ua = random.choice(ANDROID_USER_AGENTS)  # Pilih user-agent acak
        self.proxy_dict = proxy_dict
        self.current_num = 1  # Misal untuk logging
        self.total = 10  # Misal total proses yang sedang berjalan
        self.email_address = None
        self.inbox_id = None

    def log_message(self, current_num, total, message, level="info"):
        log_level = {"process": Fore.CYAN, "success": Fore.GREEN, "error": Fore.RED}
        color = log_level.get(level, Fore.WHITE)
        print(f"{color}{message}{Fore.RESET}")

    def get_random_domain(self):
        self.log_message(self.current_num, self.total, "Searching for available email domain...", "process")
        headers = {'User-Agent': self.ua}
        response = self.make_request('GET', f'https://email-fake.com/search.php?key={random.choice(string.ascii_lowercase)}', headers=headers)
        
        if not response:
            return None
            
        domains = response.json()
        valid_domains = [d for d in domains if all(ord(c) < 128 for c in d)]
        
        if valid_domains:
            selected_domain = random.choice(valid_domains)
            self.log_message(self.current_num, self.total, f"Selected domain: {selected_domain}", "success")
            return selected_domain
            
        self.log_message(self.current_num, self.total, "Could not find valid domain", "error")
        return None

    def generate_email(self, domain):
        self.log_message(self.current_num, self.total, "Generating email address...", "process")
        first_name = random.choice(string.ascii_lowercase)
        last_name = random.choice(string.ascii_lowercase)
        random_nums = ''.join(random.choices(string.digits, k=3))
        
        separator = random.choice(['', '.'])
        email = f"{first_name}{separator}{last_name}{random_nums}@{domain}"
        self.log_message(self.current_num, self.total, f"Email created: {email}", "success")
        return email

    def create_inbox(self, email):
        self.log_message(self.current_num, self.total, "Creating inbox...", "process")
        url = f"{self.base_url}/inbox"
        params = {
            'email': email
        }
        response = self.make_request('POST', url, params=params)
        
        if response:
            self.inbox_id = response.get('inbox_id')
            self.log_message(self.current_num, self.total, f"Inbox created with ID: {self.inbox_id}", "success")
            return self.inbox_id
        return None

    def get_inbox(self):
        if not self.inbox_id:
            self.log_message(self.current_num, self.total, "Inbox ID not set.", "error")
            return None
        url = f"{self.base_url}/inbox/{self.inbox_id}/messages"
        response = self.make_request('GET', url)
        
        if response and 'messages' in response:
            return response['messages']
        return []

    def get_message_token(self, message_id):
        # Token adalah message_id itu sendiri di sini
        return message_id

    def get_message_content(self, token):
        url = f"{self.base_url}/message/{token}"
        response = self.make_request('GET', url)
        
        if response:
            return response
        return {}

    def extract_otp(self, message_body):
        # Menggunakan regex untuk mencari angka 6 digit
        otp_match = re.search(r'\b\d{6}\b', message_body)
        if otp_match:
            return otp_match.group(0)
        return None

    def make_request(self, method, url, params=None, headers=None):
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, proxies=self.proxy_dict, timeout=60)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, proxies=self.proxy_dict, timeout=60)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log_message(self.current_num, self.total, f"Request failed: {response.status_code}", "error")
                return None
        except requests.exceptions.RequestException as e:
            self.log_message(self.current_num, self.total, f"Request error: {str(e)}", "error")
            return None

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message, color=Fore.WHITE, current=None, total=None):
    timestamp = f"[{Fore.LIGHTBLACK_EX}{get_timestamp()}{Style.RESET_ALL}]"
    progress = f"[{Fore.LIGHTBLACK_EX}{current}/{total}{Style.RESET_ALL}]" if current is not None and total is not None else ""
    print(f"{timestamp} {progress} {color}{message}{Style.RESET_ALL}")

def ask(message):
    return input(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def load_proxies():
    try:
        with open("proxies.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        print(f"{Fore.GREEN}\nLoaded {len(proxies)} proxies{Style.RESET_ALL}")
        return proxies
    except FileNotFoundError:
        print(f"{Fore.RED}\nFile proxies.txt not found{Style.RESET_ALL}")
        return []

def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

def generate_password():
    word = ''.join(random.choices(string.ascii_letters, k=5))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{word.capitalize()}@{numbers}#"

def send_otp(email, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/email/send_valid_email"
    payload = {
        'blockchain': "testnet",
        'email': email,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }
    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        log(f"OTP code sent to {email}", Fore.YELLOW, current, total)
        return True
    except requests.RequestException as e:
        log(f"Failed to send OTP: {e}", Fore.RED, current, total)
        return False

def verify_otp(email, valid_code, password, proxy_dict, invite_code, headers, current=None, total=None):
    url = "https://arichain.io/api/account/signup_mobile"
    payload = {
        'blockchain': "testnet",
        'email': email,
        'valid_code': valid_code,
        'pw': password,
        'pw_re': password,
        'invite_code': invite_code,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        result = response.json()
        log(f"Success Register with referral code {invite_code}", Fore.GREEN, current, total)

        with open("accounts.txt", "a") as file:
            file.write(f"ID: {result['result']['session_code']}\nEmail: {email}\nPassword: {password}\nAddress: {result['result']['address']}\nPrivate Key: {result['result']['master_key']}\n\n")

        return result['result']['address']

    except requests.RequestException as e:
        log(f"Failed to verify OTP: {e}", Fore.RED, current, total)
        return None

def daily_claim(address, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/event/checkin"
    payload = {
        'blockchain': "testnet",
        'address': address,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'success':
            log("Success claim Daily", Fore.GREEN, current, total)
            return True
        log("Daily claim failed", Fore.RED, current, total)
        return False
    except requests.exceptions.RequestException as e:
        log(f"Daily claim error: {str(e)}", Fore.RED, current, total)
        return False

def auto_send(email, to_address, password, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/wallet/transfer_mobile"
    
    payload = {
        'blockchain': "testnet",
        'symbol': "ARI",
        'email': email,
        'to_address': to_address,
        'pw': password,
        'amount': "60",
        'memo': "",
        'valid_code': "",
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success" and result.get("result") == "success":
            log(f"Success sent 60 ARI to {to_address}", Fore.GREEN, current, total)
            return True
        else:
            log(f"Failed to send: {result}", Fore.RED, current, total)
            return False
            
    except requests.RequestException as e:
        log(f"Auto-send failed: {e}", Fore.RED, current, total)
        return False

def print_banner():
    print(Fore.CYAN + """
╔═══════════════════════════════════════════╗
║         Ari Wallet Autoreferral           ║
║       https://github.com/im-hanzou        ║
╚═══════════════════════════════════════════╝
    """ + Style.RESET_ALL)

def get_referral_count():
    while True:
        try:
            count = int(ask('Enter desired number of referrals: '))
            if count > 0:
                return count
            log('Please enter a positive number.', Fore.YELLOW)
        except ValueError:
            log('Please enter a valid number.', Fore.RED)

def get_target_address():
    while True:
        # address = ask('Enter main account address for auto-send: ').strip()
        address = "ARW8aoHAoS6nAbn8dXVruS75wH5smx6obZvK1Xdwv6iYUbJ9Mf9dV"
        if address:
            return address
        log('Please enter a valid address.', Fore.YELLOW)

def get_referral_code():
    while True:
        # code = ask('Enter your referral code: ').strip()
        code ="6790105b401b3"
        if code:
            return code
        log('Please enter a valid referral code.', Fore.YELLOW)

def process_single_referral(index, total_referrals, proxy_dict, target_address, ref_code, headers):
    try:
        print(f"{Fore.CYAN}\nStarting new referral process\n{Style.RESET_ALL}")

        mail_client = TempMailClient(proxy_dict)

        # Mendapatkan domain acak dari email-fake.com
        domain = mail_client.get_random_domain()
        if not domain:
            log("Failed to find valid domain", Fore.RED, index, total_referrals)
            return False

        # Menghasilkan email dengan domain yang ditemukan
        email = mail_client.generate_email(domain)
        log(f"Generated email: {email}", Fore.CYAN, index, total_referrals)

        # Membuat inbox untuk email ini
        inbox_id = mail_client.create_inbox(email)
        if not inbox_id:
            log("Failed to create inbox.", Fore.RED, index, total_referrals)
            return False

        valid_code = None
        
        # Cek inbox untuk mencari OTP
        for _ in range(30):
            inbox = mail_client.get_inbox()
            if inbox:
                for message in inbox:
                    token = mail_client.get_message_token(message['id'])
                    content = mail_client.get_message_content(token)
                    valid_code = mail_client.extract_otp(content.get('body', ''))
                    if valid_code:
                        log(f"Found OTP: {valid_code}", Fore.GREEN, index, total_referrals)
                        break
            if valid_code:
                break
            time.sleep(2)  # Delay sebelum mencoba lagi

        if not valid_code:
            log("Failed to get OTP code.", Fore.RED, index, total_referrals)
            return False

        # Lakukan verifikasi OTP dan proses lainnya
        address = verify_otp(email, valid_code, proxy_dict, ref_code, headers, index, total_referrals)
        if not address:
            log("Failed to verify OTP.", Fore.RED, index, total_referrals)
            return False

        daily_claim(address, proxy_dict, headers, index, total_referrals)
        auto_send(email, target_address, proxy_dict, headers, index, total_referrals)
        
        log(f"Referral #{index} completed!", Fore.MAGENTA, index, total_referrals)
        return True
        
    except Exception as e:
        log(f"Error occurred: {str(e)}.", Fore.RED, index, total_referrals)
        return False

def main():
    print_banner()
    
    ref_code = get_referral_code()
    if not ref_code:
        return

    total_referrals = get_referral_count()
    if not total_referrals:
        return
        
    target_address = get_target_address()
    if not target_address:
        return

    proxies = load_proxies()
    headers = {
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'User-Agent': random.choice(ANDROID_USER_AGENTS)
    }
    
    successful_referrals = 0
    for index in range(1, total_referrals + 1):
        proxy = get_random_proxy(proxies)
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None
        
        if process_single_referral(index, total_referrals, proxy_dict, target_address, ref_code, headers):
            successful_referrals += 1
    
    print(f"{Fore.MAGENTA}\nCompleted {successful_referrals}/{total_referrals} successful referrals{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\nScript terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}\nAn unexpected error occurred: {str(e)}{Style.RESET_ALL}")
    finally:
        print(f"{Fore.CYAN}\nAll Process completed{Style.RESET_ALL}")
