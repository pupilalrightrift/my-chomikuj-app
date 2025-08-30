from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'chomik-secret-key-2025'

class ChomikujClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.logged_in = False
        self.username = None

    def login(self, username, password):
        try:
            # 1) Pobierz stronę logowania
            resp = self.session.get('https://chomikuj.pl/action/Login', timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 2) Znajdź formularz
            form = soup.find('form')
            if not form:
                return False, 'Nie znaleziono formularza logowania'

            # 3) Zbierz dane z pól
            data = {}
            for inp in form.find_all('input'):
                name = inp.get('name')
                if not name:
                    continue
                data[name] = inp.get('value', '')

            data['Login'] = username
            data['Password'] = password

            # 4) Wyślij dane do endpointu TopBarLogin
            post_resp = self.session.post(
                'https://chomikuj.pl/action/Login/TopBarLogin',
                data=data, timeout=10
            )
            post_resp.raise_for_status()

            # 5) Sprawdź odpowiedź
            text = post_resp.text.lower()
            if username.lower() in text or 'wyloguj' in text:
                self.logged_in = True
                self.username = username
                return True, 'Pomyślnie zalogowano'
            else:
                return False, 'Nieprawidłowy login lub hasło'

        except requests.exceptions.Timeout:
            return False, 'Przekroczono czas oczekiwania na odpowiedź'
        except requests.exceptions.RequestException as e:
            return False, f'Błąd sieci: {e}'
        except Exception as e:
            return False, f'Błąd wewnętrzny: {e}'

    def get_user_info(self):
        if not self.logged_in:
            return None
        return {
            'username': self.username,
            'status': 'Zalogowany na Chomikuj.pl'
        }

chomik_client = ChomikujClient()

@app.route('/', methods=['GET'])
def home():
    if chomik_client.logged_in:
        info = chomik_client.get_user_info()
        return render_template('dashboard.html', user_info=info)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    if not username or not password:
        flash('Podaj login i hasło', 'error')
        return redirect(url_for('home'))

    success, message = chomik_client.login(username, password)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    chomik_client.logged_in = False
    chomik_client.username = None
    flash('Wylogowano', 'info')
    return redirect(url_for('home'))

@app.route('/browse')
def browse():
    if not chomik_client.logged_in:
        flash('Zaloguj się najpierw', 'error')
        return redirect(url_for('home'))
    return render_template('browse.html', username=chomik_client.username)
