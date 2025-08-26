import requests
import socket
from config import *

def test_network():
    print("Testing network connectivity...")
    
    # Test basic internet
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        print(f"✅ Internet connection: OK (IP: {response.json()['origin']})")
    except Exception as e:
        print(f"❌ Internet connection: FAILED - {e}")
        return False
    
    # Test Telegram API connectivity
    try:
        response = requests.get("https://api.telegram.org", timeout=10)
        print(f"✅ Telegram API: OK (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Telegram API: FAILED - {e}")
        return False
    
    # Test bot token
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot token: OK (Bot: @{bot_info['result']['username']})")
        else:
            print(f"❌ Bot token: INVALID - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Bot token test: FAILED - {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_network():
        print("\n🎉 All connectivity tests passed!")
    else:
        print("\n💥 Some tests failed. Check your network connection.")