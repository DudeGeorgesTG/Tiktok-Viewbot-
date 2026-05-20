import os
import random
import secrets
import time
import uuid
import binascii
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List

import requests
import SignerPy


@dataclass
class DeviceInfo:
    model: str
    brand: str
    build: str


def generate_device_info() -> DeviceInfo:
    device_pool: List[tuple[str, str]] = [
        ("SM-A127F", "samsung"), ("SM-A325F", "samsung"), ("SM-A525F", "samsung"),
        ("SM-A725F", "samsung"), ("SM-G780G", "samsung"), ("SM-G990B", "samsung"),
        ("SM-S901B", "samsung"), ("SM-S908B", "samsung"), ("SM-N981B", "samsung"),
        ("SM-N986B", "samsung"), ("Pixel 6", "google"), ("Pixel 7", "google"),
        ("Pixel 8", "google"), ("OnePlus 9", "oneplus"), ("OnePlus 10", "oneplus"),
        ("Xiaomi Mi 11", "xiaomi"), ("Xiaomi 12", "xiaomi"), ("Realme 8", "realme"),
        ("Realme 9", "realme"), ("POCO F3", "xiaomi")
    ]
    
    builds: List[str] = [
        "RP1A.200720.011", "RP1A.200720.012", "SP1A.210812.016",
        "TP1A.220624.014", "TQ1A.230205.002", "TQ2A.230505.002",
        "UKQ1.230804.001", "AP2A.240605.024"
    ]
    
    model, brand = random.choice(device_pool)
    build = random.choice(builds)
    
    return DeviceInfo(model=model, brand=brand, build=build)


class TikTokViewBot:
    def __init__(self, session_id: str, video_id: str, device_info: DeviceInfo):
        self.session_id = session_id
        self.video_id = video_id
        self.device = device_info
        self.csrf_token = secrets.token_hex(16)
        
        self.cookies = {
            'sessionid': session_id,
            'sid_tt': session_id,
            'passport_csrf_token': self.csrf_token,
            'passport_csrf_token_default': self.csrf_token,
        }
        
        self.headers = {
            'User-Agent': (
                f'com.tiktok.lite.go/390054 (Linux; U; Android 13; en_GB; '
                f'{self.device.model}; Build/{self.device.build}; tt-ok/3.12.13.34-ul)'
            ),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
    
    def _build_params(self) -> Dict[str, str]:
        timestamp = int(time.time())
        return {
            "device_id": str(random.randint(10**17, 10**19)),
            "iid": str(random.randint(10**17, 10**19)),
            "openudid": binascii.hexlify(os.urandom(8)).decode(),
            "cdid": str(uuid.uuid4()),
            "app_name": "musical_ly",
            "version_code": "390603",
            "version_name": "39.6.3",
            "app_version": "39.6.3",
            "manifest_version_code": "2023906030",
            "update_version_code": "2023906030",
            "ab_version": "39.6.3",
            "resolution": "1080*2220",
            "dpi": "440",
            "device_platform": "android",
            "device_type": self.device.model,
            "device_brand": self.device.brand,
            "os_api": "30",
            "os_version": "11",
            "os": "android",
            "host_abi": "arm64-v8a",
            "language": "ar",
            "locale": "ar",
            "region": "EG",
            "current_region": "YE",
            "sys_region": "EG",
            "carrier_region": "YE",
            "residence": "YE",
            "app_language": "ar",
            "app_type": "normal",
            "channel": "googleplay",
            "aid": "1233",
            "ts": str(timestamp),
            "_rticket": str(timestamp * 1000),
            "play_delta": "1",
            "stats_channel": "play",
            "item_id": self.video_id,
        }
    
    def send_view(self) -> bool:
        params = self._build_params()
        signature = SignerPy.sign(params=params, cookie=self.cookies)
        
        headers = self.headers.copy()
        headers['x-tt-passport-csrf-token'] = self.csrf_token
        headers.update(signature)
        headers['Cookie'] = '; '.join(f'{k}={v}' for k, v in self.cookies.items())
        
        url = 'https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/'
        response = requests.post(url, params=params, headers=headers, cookies=self.cookies)
        
        return response.json().get('status_code') == 0


def load_sessions(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def main() -> None:
    SESSION_FILE = 'sessionids.txt'
    VIDEO_ID = input('[!] VideoID: ')
    MAX_WORKERS = 500
    
    sessions = load_sessions(SESSION_FILE)
    
    device_info = generate_device_info()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            for session_id in sessions:
                bot = TikTokViewBot(session_id, VIDEO_ID, device_info)
                executor.submit(bot.send_view)


if __name__ == '__main__':
    main()
