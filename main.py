import tls_client 
import random
import time
import re
import toml
import ctypes
import threading
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

from functools import wraps
from logmagix import Logger, Home

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)
log = Logger()

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                log.debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.failure("Proxy file not found. Running in proxyless mode.")
            return None
    
    @debug 
    def generate_email(self, domain: str = "dpptd.com") -> str:
        username = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=30))}"
        email = f"{username}@{domain}"
        return email

    class Title:
        def __init__(self) -> None:
            self.running = False

        def start_title_updates(self, total, start_time) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.update_title(total, start_time)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stop_title_updates(self) -> None:
            self.running = False

        def update_title(self, total, start_time) -> None:
            try:
                elapsed_time = round(time.time() - start_time, 2)
                title = f'discord.cyberious.xyz | Total: {total} | Time Elapsed: {elapsed_time}s'

                sanitized_title = ''.join(c if c.isprintable() else '?' for c in title)
                ctypes.windll.kernel32.SetConsoleTitleW(sanitized_title)
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class EmailHandler:
    def __init__(self, proxy_dict: dict = None) -> None:
        self.session = tls_client.Session(random_tls_extension_order=True)
        self.session.proxies = proxy_dict

    @debug
    def check_mailbox(self, username: str, domain: str, max_retries: int = 5) -> list | None:
        debug(f"Checking mailbox for {username}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}')
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    log.warning(f"503 error encountered, retrying ({attempt + 1}/{max_retries})")
                    time.sleep(2 * (attempt + 1)) 
                    continue
                else:
                    log.failure(f"Failed to check mailbox: {response.text}, {response.status_code}")
                    debug(response.json(), response.status_code)
                    break
            except Exception as e:
                log.failure(f"Error checking mailbox: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
        return None

    @debug
    def fetch_message(self, username: str, domain: str, id: int, max_retries: int = 5) -> dict | None:
        debug(f"Fetching mailbox message for {username}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={id}')
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    log.warning(f"503 error encountered, retrying ({attempt + 1}/{max_retries})")
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    log.failure(f"Failed to fetch message: {response.text}, {response.status_code}")
                    break
            except Exception as e:
                log.failure(f"Error fetching message: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
        return None

    @debug
    def get_mail_id(self, username: str, domain: str) -> int | None:
        attempt = 0
        debug(f"Getting verification message id for {username}")
        while attempt < 10: 
            messages = self.check_mailbox(username, domain)
            if messages:
                for message in messages:
                    if 'Sign in to Character.AI' in message.get("subject", ""):
                        debug(message)
                        return message.get("id")
            attempt += 1
            time.sleep(1.5)
        debug(f"No verification message found after {attempt} attempts")
        return None 

    @debug
    def get_verification_url(self, email: str) -> str | None:
        debug(f"Getting verification code for {email}")
        
        username, domain = email.split("@")

        mail_id = self.get_mail_id(username, domain)
        if mail_id:
            message = self.fetch_message(username, domain, mail_id)
            login_url_match = re.search(r'https://character\.ai/login/[a-f0-9-]+', message.get("body"))
            if login_url_match:
                login_url = login_url_match.group(0)
                return login_url
        return None

class AccountCreator:
    def __init__(self, proxy_dict: dict = None) -> None:
        self.session = tls_client.Session("okhttp4_android_13", random_tls_extension_order=True)
        self.session.proxies = proxy_dict
    
    @debug
    def send_verification_email(self, email: str) -> bool:
        debug("Sending request to email verification url")

        response = self.session.get(f'https://character.ai/login/send?email={email}&app=true&host=https://character.ai')
        debug_response(response)
        
        if response.status_code == 200:
            if response.json().get("result"):
                return True
            else:
                log.failure("Failed to get result from json")
        else:
            log.failure(f"Failed to send the email verification url: {response.status_code}, {response.text}")

        return False
    
    @debug
    def verify_email(self, url: str) -> str | None:
        debug("Sending request to verify email")
        
        response = self.session.get(url)
        debug_response(response)
        
        if response.status_code == 200:
            oob_code = re.search(r'oobCode=(.*?)(?:&|\\u0026)', response.text).group(1)

            if oob_code:
                debug(oob_code)
                return oob_code
            else:
                log.failure("Failed to extract oob code from response")
        else:
            log.failure(f"Failed to verify email address: {response.status_code}")
        
        return None
    
    @debug    
    def get_jwt(self, email: str, oob_code: str) -> str | None:
        debug("Getting JWT token")

        params = {
            'key': 'AIzaSyBYjIdjN5T49bIWDGX00qyr_WMlRRVeMMU', # Static
        }

        json_data = {
            'email': email,
            'oobCode': oob_code,
            'clientType': 'CLIENT_TYPE_ANDROID',
        }
        
        response = self.session.post(
                'https://www.googleapis.com/identitytoolkit/v3/relyingparty/emailLinkSignin',
                params=params,
                json=json_data,
            )
        
        debug_response(response)
        
        if response.status_code == 200:
            token = response.json().get("idToken")

            if token:
                return token
            else:
                log.failure("Failed to extract jwt token from response")
        else:
            log.failure(f"Failed to get jwt token: {response.status_code}, {response.text}")
        
        return None
    
    @debug
    def get_authentification_key(self, jwt: str) -> str | None:
        debug("Sending request to get auth key")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        json_data = {'id_token': jwt}

        try:
            response = self.session.post(
                'https://plus.character.ai/dj-rest-auth/google_idp/',
                headers=headers,
                json=json_data
            )

            debug_response(response)

            if response.status_code == 200:
                key = response.json().get("key")
                if key:
                    return key
                else:
                    log.failure("Failed to extract authentication key")
            else:
                log.failure(f"Failed to get authentication key {response.text}, {response.status_code}")
        except Exception as e:
            log.failure(f"Request failed: {str(e)}")
            
        return None

    @debug
    def signup(self, key: str) -> bool:
        debug("Sending request to singup")
        
        headers = {
            'authorization': f'Token {key}',
        }

        json_data = {
            'username': '',
            'date_of_birth': f"{random.randint(1965, 2006)}-{str(random.randint(1, 12)).zfill(2)}-{str(random.randint(1, 28)).zfill(2)}T00:00:00.000Z",
            'userInEEA': True,
            'userInUK': True,
            'date_of_birth_collected': True,
            'acknowledgement': True,
            'name': '',
            'avatar_type': '',
            'avatar_file_name': '',
            'auto_username': True,
            'signup_code': '',
        }

        response = self.session.post('https://beta.character.ai/chat/user/signup/', headers=headers, json=json_data)

        debug_response(response)

        if response.status_code == 200:
            if response.json().get("status") == "OK":
                return True
        else:
            log.failure(f"Failed to sign up: {response.text}, {response.status_code}")
        return False

def create_account() -> bool:
    try:
        account_start_time = time.time()

        Misc = Miscellaneous()
        proxies = Misc.get_proxies()
        Email_Handler = EmailHandler(proxies)
        Account_Generator = AccountCreator(proxies)
        
        email = Misc.generate_email()
        
        log.info(f"Starting a new account creation process for {email[:8]}...")
        if Account_Generator.send_verification_email(email):
            url = Email_Handler.get_verification_url(email)

            if url:
                log.info("Verifying email...")
                oob_code = Account_Generator.verify_email(url)

                if oob_code:
                    jwt = Account_Generator.get_jwt(email, oob_code)

                    if jwt:
                        key = Account_Generator.get_authentification_key(jwt)

                        if key:
                           log.info("Validating account...")
                           if Account_Generator.signup(key):
                                with open("output/accounts.txt", "a") as f:
                                   f.write(f"{email}\n")
                        
                                log.message("Character.ai", f"Account successfully created {email[:8]}...", account_start_time, time.time())
                                return True
        return False
    except Exception as e:
        log.failure(f"Error during account creation process: {e}")
        return False

def main() -> None:
    try:
        start_time = time.time()
        
        # Initialize basic classes
        Misc = Miscellaneous()
        Banner = Home("C.AI Generator", align="center", credits="discord.cyberious.xyz")
        
        # Display Banner
        Banner.display()

        total = 0
        thread_count = config['dev'].get('Threads', 1)

        # Start updating the title
        title_updater = Misc.Title()
        title_updater.start_title_updates(total, start_time)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            while True:
                futures = [
                    executor.submit(create_account)
                    for _ in range(thread_count)
                ]

                for future in as_completed(futures):
                    try:
                        if future.result():
                            total += 1
                    except Exception as e:
                        log.failure(f"Thread error: {e}")

    except KeyboardInterrupt:
        log.info("Process interrupted by user. Exiting...")
    except Exception as e:
        log.failure(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()