import sys
import time
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, QAction, 
                             QVBoxLayout, QWidget, QTextEdit, QListWidget, QListWidgetItem, 
                             QComboBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt

# Selenium pour YouTube (mode headless)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gyros")
        self.setGeometry(100, 100, 1200, 800)

        # Vue principale du navigateur
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Barre d'adresse
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Barre de navigation classique
        self.navigation_toolbar = QToolBar()
        self.addToolBar(self.navigation_toolbar)

        back_btn = QAction("Précédent", self)
        back_btn.triggered.connect(self.browser.back)
        self.navigation_toolbar.addAction(back_btn)

        forward_btn = QAction("Suivant", self)
        forward_btn.triggered.connect(self.browser.forward)
        self.navigation_toolbar.addAction(forward_btn)

        refresh_btn = QAction("Actualiser", self)
        refresh_btn.triggered.connect(self.browser.reload)
        self.navigation_toolbar.addAction(refresh_btn)

        cookie_btn = QAction("Afficher Cookies", self)
        cookie_btn.triggered.connect(self.show_cookies)
        self.navigation_toolbar.addAction(cookie_btn)

        # Ajout de la barre d'adresse
        self.navigation_toolbar.addWidget(self.url_bar)

        # Barre de recherche dédiée
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher...")
        self.search_bar.returnPressed.connect(self.perform_search)
        self.navigation_toolbar.addWidget(self.search_bar)

        # ComboBox pour choisir la plateforme de recherche
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Wikipedia", "YouTube", "StackOverflow", "Reddit", "Medium"])
        self.navigation_toolbar.addWidget(self.platform_combo)

        # Historique
        self.history = []

        # Gestion des cookies
        self.cookie_store = QWebEngineProfile.defaultProfile().cookieStore()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))
        self.history.append(url)

    def show_cookies(self):
        self.cookies_window = QWidget()
        self.cookies_window.setWindowTitle("Cookies")
        self.cookies_window.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.cookies_text = QTextEdit()
        self.cookies_text.setReadOnly(True)
        layout.addWidget(self.cookies_text)
        self.cookies_window.setLayout(layout)

        self.cookies_text.setText("Chargement des cookies...\n")
        self.cookie_store.cookieAdded.connect(self.add_cookie_to_display)

        self.cookies_window.show()

    def add_cookie_to_display(self, cookie):
        cookie_data = (
            f"Nom: {cookie.name().data().decode()}\n"
            f"Valeur: {cookie.value().data().decode()}\n"
            f"Domaine: {cookie.domain()}\n"
            f"Chemin: {cookie.path()}\n"
            f"Expiration: {cookie.expirationDate().toString()}\n\n"
        )
        self.cookies_text.append(cookie_data)

    def perform_search(self):
        query = self.search_bar.text().strip()
        if not query:
            return

        platform = self.platform_combo.currentText()
        if platform == "Wikipedia":
            results = self.search_wikipedia(query)
        elif platform == "YouTube":
            results = self.search_youtube(query)
        elif platform == "StackOverflow":
            results = self.search_stackoverflow(query)
        elif platform == "Reddit":
            results = self.search_reddit(query)
        elif platform == "Medium":
            results = self.search_medium(query)
        else:
            results = []

        if results:
            self.display_search_results(results)
        else:
            QMessageBox.information(self, "Aucun résultat", "Aucun résultat trouvé.")

    def search_wikipedia(self, query):
        url = f"https://fr.wikipedia.org/w/index.php?search={query}"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            # Recherche de résultats classiques
            search_results = soup.find_all("div", class_="mw-search-result-heading")
            if search_results:
                for item in search_results:
                    a_tag = item.find("a")
                    if a_tag and "href" in a_tag.attrs:
                        title = a_tag.get_text(strip=True)
                        link = "https://fr.wikipedia.org" + a_tag["href"]
                        results.append((title, link))
            else:
                # Vérifier s'il s'agit directement d'un article
                first_heading = soup.find("h1", id="firstHeading")
                if first_heading:
                    title = first_heading.get_text(strip=True)
                    link = response.url
                    results.append((title, link))
            return results
        except Exception as e:
            print("Erreur lors de la recherche sur Wikipedia:", e)
            return []

    def search_youtube(self, query):
        url = f"https://www.youtube.com/results?search_query={query}"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            # Attendre que l'élément contenant les résultats soit présent
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "contents")))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            results = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if href.startswith("/watch") and a_tag.get("title"):
                    title = a_tag.get("title")
                    link = "https://www.youtube.com" + href
                    results.append((title, link))
            # Filtrer les doublons
            seen = set()
            filtered_results = []
            for title, link in results:
                if link not in seen:
                    filtered_results.append((title, link))
                    seen.add(link)
            return filtered_results
        except Exception as e:
            print("Erreur lors de la recherche sur YouTube avec Selenium:", e)
            return []
        finally:
            if driver:
                driver.quit()

    def search_stackoverflow(self, query):
        url = f"https://stackoverflow.com/search?q={query}"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            # Recherche des questions via la classe "question-summary"
            for question in soup.find_all("div", class_="question-summary"):
                a_tag = question.find("a", class_="question-hyperlink")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = "https://stackoverflow.com" + a_tag["href"]
                    results.append((title, link))
            return results
        except Exception as e:
            print("Erreur lors de la recherche sur StackOverflow:", e)
            return []

    def search_reddit(self, query):
        url = f"https://www.reddit.com/search/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            # Recherche des liens ayant l'attribut data-click-id égal à "body"
            for a_tag in soup.find_all("a", attrs={"data-click-id": "body"}):
                title = a_tag.get_text(strip=True)
                link = a_tag.get("href")
                if link and not link.startswith("http"):
                    link = "https://www.reddit.com" + link
                if title and link:
                    results.append((title, link))
            # Filtrer les doublons
            seen = set()
            filtered_results = []
            for title, link in results:
                if link not in seen:
                    filtered_results.append((title, link))
                    seen.add(link)
            return filtered_results
        except Exception as e:
            print("Erreur lors de la recherche sur Reddit:", e)
            return []

    def search_medium(self, query):
        url = f"https://medium.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            # Recherche des articles via une classe typique (la structure peut varier)
            for div in soup.find_all("div", class_="postArticle-content"):
                a_tag = div.find("a")
                if a_tag and a_tag.get("href"):
                    title = a_tag.get_text(strip=True)
                    link = a_tag["href"].split("?")[0]
                    results.append((title, link))
            return results
        except Exception as e:
            print("Erreur lors de la recherche sur Medium:", e)
            return []

    def display_search_results(self, results):
        self.results_window = QWidget()
        self.results_window.setWindowTitle("Résultats de recherche")
        self.results_window.setGeometry(150, 150, 800, 600)
        layout = QVBoxLayout()
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        self.results_window.setLayout(layout)

        for title, link in results:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, link)
            self.results_list.addItem(item)

        self.results_list.itemDoubleClicked.connect(self.load_search_result)
        self.results_window.show()

    def load_search_result(self, item):
        link = item.data(Qt.UserRole)
        self.browser.setUrl(QUrl(link))
        self.results_window.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
