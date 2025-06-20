import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from colorama import init

from config import RETRY_COUNT, BACKOFF_FACTOR, STATUS_FORCELIST, TIMEOUT

# Inisialisasi colorama
init(autoreset=True)

# Disable peringatan InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_session_with_retries():
    """Fungsi untuk setup requests session dengan retry."""
    session = requests.Session()
    retry = Retry(
        total=RETRY_COUNT,
        read=RETRY_COUNT,
        connect=RETRY_COUNT,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=STATUS_FORCELIST,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def check_plesk_login(url, username, password):
    """
    Fungsi pengecekan login Plesk.
    Mengembalikan tuple (url, username, password, status) jika berhasil,
    atau string "FAILED" / "TIMEOUT" jika gagal.
    """
    session = get_session_with_retries()
    login_url = url + '/login_up.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'login_name': username,
        'passwd': password
    }
    
    try:
        response = session.post(login_url, headers=headers, data=data, timeout=TIMEOUT, verify=False)
        
        if response.status_code == 200 and 'logout.php' in response.text:
            if 'no subscriptions' in response.text.lower():
                return (url, username, password, "NO SUBSCRIPTIONS")
            elif 'items total' in response.text.lower():
                return (url, username, password, "ACTIVE")
            elif 'was suspended' in response.text.lower():
                return (url, username, password, "SUSPENDED")
            else:
                return (url, username, password, "ACTIVE")
        else:
            return "FAILED"
    except requests.exceptions.RequestException:
        return "TIMEOUT"
