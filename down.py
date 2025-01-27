import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QAction, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gyros")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

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

        self.navigation_toolbar.addWidget(self.url_bar)
        self.history = []

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


    def handle_cookies(self, cookies):
        cookies_info = []
        for cookie in cookies:
            cookie_data = (
                f"Nom: {cookie.name().data().decode()}\n"
                f"Valeur: {cookie.value().data().decode()}\n"
                f"Domaine: {cookie.domain()}\n"
                f"Chemin: {cookie.path()}\n"
                f"Expiration: {cookie.expirationDate().toString()}\n\n"
            )
            cookies_info.append(cookie_data)
        self.cookies_text.setText("\n".join(cookies_info))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
