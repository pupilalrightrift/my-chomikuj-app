
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
app.secret_key = 'chomik-secret-key-2025'  

class ChomikujClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logged_in = False
        self.username = None

    def login(self, username, password):
        """Loguje się do Chomikuj.pl"""
        try:
            # Krok 1: Pobierz stronę logowania
            login_page = self.session.get('https://chomikuj.pl/action/Login')
            if login_page.status_code != 200:
                return False, "Nie można pobrać strony logowania"

            # Krok 2: Wyodrębnij formularz logowania
            soup = BeautifulSoup(login_page.text, 'html.parser')

            # Znajdź wszystkie ukryte pola formularza
            login_form = soup.find('form')
            if not login_form:
                return False, "Nie znaleziono formularza logowania"

            form_data = {}
            for input_field in login_form.find_all('input'):
                if input_field.get('name') and input_field.get('value'):
                    form_data[input_field.get('name')] = input_field.get('value')

            # Dodaj dane logowania
            form_data['Login'] = username
            form_data['Password'] = password

            # Krok 3: Wyślij dane logowania
            login_response = self.session.post(
                'https://chomikuj.pl/action/Login/TopBarLogin',
                data=form_data,
                allow_redirects=True
            )

            # Krok 4: Sprawdź czy logowanie się powiodło
            if login_response.status_code == 200:
                # Sprawdź czy w odpowiedzi jest komunikat o sukcesie
                if 'wyloguj' in login_response.text.lower() or username.lower() in login_response.text.lower():
                    self.logged_in = True
                    self.username = username
                    return True, "Pomyślnie zalogowano!"
                else:
                    return False, "Nieprawidłowe dane logowania"
            else:
                return False, f"Błąd serwera: {login_response.status_code}"

        except Exception as e:
            return False, f"Błąd połączenia: {str(e)}"

    def get_user_info(self):
        """Pobiera informacje o użytkowniku"""
        if not self.logged_in:
            return None

        try:
            profile_page = self.session.get('https://chomikuj.pl')
            if profile_page.status_code == 200:
                soup = BeautifulSoup(profile_page.text, 'html.parser')
                # Szukaj informacji o użytkowniku na stronie
                user_info = {
                    'username': self.username,
                    'logged_in': True,
                    'status': 'Połączony z Chomikuj.pl'
                }
                return user_info
        except:
            pass

        return {'username': self.username, 'logged_in': True, 'status': 'Zalogowany'}

# Globalna instancja klienta
chomik_client = ChomikujClient()

@app.route('/')
def home():
    """Strona główna"""
    if chomik_client.logged_in:
        user_info = chomik_client.get_user_info()
        return render_template('dashboard.html', user_info=user_info)
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Strona logowania do Chomikuj.pl"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Próba logowania do Chomikuj.pl
        success, message = chomik_client.login(username, password)

        if success:
            session['chomik_logged_in'] = True
            session['chomik_username'] = username
            flash(message, 'success')
            return redirect(url_for('home'))
        else:
            flash(message, 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Wylogowanie"""
    chomik_client.logged_in = False
    chomik_client.username = None
    session.pop('chomik_logged_in', None)
    session.pop('chomik_username', None)
    flash('Zostałeś wylogowany z Chomikuj.pl', 'info')
    return redirect(url_for('home'))

@app.route('/browse')
def browse():
    """Przeglądaj pliki (przykład)"""
    if not chomik_client.logged_in:
        flash('Musisz się najpierw zalogować!', 'error')
        return redirect(url_for('login'))

    # Tu możesz dodać kod do przeglądania plików
    return render_template('browse.html', username=chomik_client.username)

# WAŻNE: Usuń app.run() - nie działa na PythonAnywhere!
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
