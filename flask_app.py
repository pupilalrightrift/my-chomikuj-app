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
        # ... (bez zmian; poprzednia wersja) ...
        # po poprawnej autoryzacji:
        self.logged_in = True
        self.username = username
        return True, 'Pomyślnie zalogowano'

    def list_files(self):
        """
        Pobiera listę plików z głównej strony użytkownika.
        Zwraca listę słowników: [{'name':..., 'url':...}, ...]
        """
        if not self.logged_in:
            return []
        resp = self.session.get('https://chomikuj.pl/' + self.username, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        files = []
        # Zakładamy, że pliki są w tabeli lub divach z linkami do pobrania
        for a in soup.select('a.filename'):  
            name = a.text.strip()
            url = a['href']
            files.append({'name': name, 'url': url})

        return files

    def get_user_info(self):
        if not self.logged_in:
            return None
        return {'username': self.username, 'status': 'Zalogowany na Chomikuj.pl'}

chomik_client = ChomikujClient()

# ... trasy / i /login, /logout bez zmian ...

@app.route('/browse')
def browse():
    if not chomik_client.logged_in:
        flash('Zaloguj się najpierw', 'error')
        return redirect(url_for('home'))

    try:
        files = chomik_client.list_files()
    except Exception as e:
        flash(f'Błąd pobierania listy plików: {e}', 'error')
        files = []

    return render_template('browse.html',
                           username=chomik_client.username,
                           files=files)


    
    try:
        files = chomik_client.list_files()
    except Exception as e:
        flash(f'Błąd pobierania listy plików: {e}', 'error')
        files = []

    return render_template('browse.html',
                           username=chomik_client.username,
                           files=files)


