import requests
import random
import time
import string
import names
from colorama import Fore, Style, init
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

init()
ua = UserAgent()
file_name = "response_output.txt"

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

model = None
successful_accounts = 0
failed_accounts = 0
MAX_RETRIES = 10

def get_headers(token=None):
    headers = {
        'accept': '/',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=1, i',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': ua.chrome
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

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

        # Dapatkan domain email acak dari fake-mail
        domain = get_random_domain(proxy_dict)
        if not domain:
            log("Failed to get a valid domain", Fore.RED, index, total_referrals)
            return False

        # Buat email baru dengan domain yang dipilih
        email = generate_email(domain)
        password = generate_password()
        log(f"Generated account: {email}:{password}", Fore.CYAN, index, total_referrals)

        # Kirim OTP ke email
        if not send_otp(email, proxy_dict, headers, index, total_referrals):
            log("Failed to send OTP.", Fore.RED, index, total_referrals)
            return False

        # Tunggu OTP masuk ke inbox
        valid_code = get_otp(email, domain, proxy_dict)
        if not valid_code:
            log("Failed to retrieve OTP.", Fore.RED, index, total_referrals)
            return False

        # Verifikasi OTP
        address = verify_otp(email, valid_code, password, proxy_dict, ref_code, headers, index, total_referrals)
        if not address:
            log("Failed to verify OTP.", Fore.RED, index, total_referrals)
            return False

        # Lakukan langkah tambahan seperti daily claim atau auto-send
        daily_claim(address, proxy_dict, headers, index, total_referrals)
        auto_send(email, target_address, password, proxy_dict, headers, index, total_referrals)

        log(f"Referral #{index} completed!", Fore.MAGENTA, index, total_referrals)
        return True

    except Exception as e:
        log(f"Error occurred: {str(e)}.", Fore.RED, index, total_referrals)
        log(f"Full exception details: {repr(e)}", Fore.RED, index, total_referrals)
        return False

def get_random_domain(proxies):
    log_message("Searching for available email domain...", "process")
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    keyword = random.choice(consonants) + random.choice(vowels)

    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            response = requests.get(
                f'https://generator.email/search.php?key={keyword}',
                headers=get_headers(),
                proxies=proxies,
                timeout=120
            )
            domains = response.json()
            valid_domains = [d for d in domains if all(ord(c) < 128 for c in d)]

            if valid_domains:
                selected_domain = random.choice(valid_domains)
                log_message(f"Selected domain: {selected_domain}", "success")
                return selected_domain

            log_message("Could not find valid domain", "error")
            return None

        except Exception as e:
            retry_count += 1
            if retry_count < MAX_RETRIES:
                log_message(f"Connection error: {str(e)}. Retrying... ({retry_count}/{MAX_RETRIES})", "warning")
            else:
                log_message(f"Error getting domain after {MAX_RETRIES} attempts: {str(e)}", "error")
                return None

def log_message(message: str, message_type: str = "info"):
    """
    Log a message with a specified type.

    :param message: The message to log
    :param message_type: The type of the message ('info', 'success', 'warning', 'error', 'process')
    """
    colors = {
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "process": Fore.CYAN,
    }
    color = colors.get(message_type, Fore.WHITE)
    print(f"{color}[{message_type.upper()}] {message}{Style.RESET_ALL}")

def generate_email(domain):
    log_message("Generating email address...", "process")
    first_name = names.get_first_name().lower()
    last_name = names.get_last_name().lower()
    random_nums = ''.join(random.choices(string.digits, k=3))

    separator = random.choice(['', '.'])
    email = f"{first_name}{separator}{last_name}{random_nums}@{domain}"
    log_message(f"Email created: {email}", "success")
    return email

def get_otp(email, domain, proxies):
    log_message("Waiting for OTP email...", "process")
    cookies = {
        'embx': f'[%22{email}%22]',
        'surl': f'{domain}/{email.split("@")[0]}'
    }

    max_attempts = 5
    retry_count = 0

    while retry_count < max_attempts:
        try:
            response = requests.get(
                'https://generator.email/inbox4/',
                headers=get_headers(),
                cookies=cookies,
                proxies=proxies,
                timeout=120
            )

            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(response.text)

            soup = BeautifulSoup(response.text, 'html.parser')
            mailextra = soup.find('p', {'class': 'mailextra'})

            if mailextra:
                otp_text = mailextra.text.strip()

                # Cari angka 6 digit langsung dalam teks tanpa menggunakan regex
                otp = ''.join(filter(str.isdigit, otp_text))[:6]  # Ambil 6 digit pertama
                if otp and len(otp) == 6:
                    log_message(f"OTP found: {otp}", "success")
                    return otp

            log_message(f"Attempt {retry_count + 1}: Waiting for email with OTP...", "process")
            retry_count += 1
            time.sleep(10)  # Tunggu sebelum mencoba lagi

        except Exception as e:
            retry_count += 1
            if retry_count < max_attempts:
                log_message(f"Connection error while getting OTP: {str(e)}. Retrying... ({retry_count}/{max_attempts})", "warning")
            else:
                log_message(f"Error getting OTP after {max_attempts} attempts: {str(e)}", "error")
                return None

    log_message("Could not find OTP", "error")
    return None

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
