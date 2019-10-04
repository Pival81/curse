from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
import requests
import bs4
from urllib import parse


class RestrictedQWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    """ Filters links so that users cannot just navigate to any page on the web,
    but just to those pages, that are listed in allowed_pages.
    This is achieved by re-implementing acceptNavigationRequest.
    The latter could also be adapted to accept, e.g. URLs within a domain."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.allowed = True

    def acceptNavigationRequest(self, qurl, navtype, mainframe):
        # print("Navigation Request intercepted:", qurl)
        if self.allowed:  # open in QWebEngineView
            self.allowed = False
            return True
        else:  # delegate link to default browser
            QtGui.QDesktopServices.openUrl(qurl)
            return False


class RestrictedWebViewWidget(QtWidgets.QWidget):
    """A QWebEngineView is required to display a QWebEnginePage."""

    def __init__(self, parent=None, url=None):
        super().__init__(parent)
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.page = RestrictedQWebEnginePage()
        self.html = self.getHTMLCorrected(url)
        self.page.setHtml(self.html)

        # associate page with view
        self.view.setPage(self.page)

        # set layout
        self.vl = QtWidgets.QVBoxLayout()
        self.vl.addWidget(self.view)
        self.setLayout(self.vl)

        # set minimum size
        self.setMinimumSize(1200, 600)

    def getHTMLCorrected(self, url):
        headers = {"User-Agent": "CurseClient/7.5 (Microsoft Windows NT 6.1.7600.0) CurseClient/7.5.7208.4378"}
        html = requests.get(url, headers=headers)
        soup_obj = bs4.BeautifulSoup(html.text, 'lxml')
        links = soup_obj.find_all('a')
        for link in links:
            if link.get("href").startswith("/linkout?remoteUrl="):
                link["href"] = link["href"].replace("/linkout?remoteUrl=", "")
                link["href"] = parse.unquote(parse.unquote(link["href"]))
        with open("buh.html", "w") as html_file:
            html_file.write(str(soup_obj))
        return str(soup_obj)

class Main():
	
	def __init__(self, id):
		import sys
		app = QtWidgets.QApplication(sys.argv)
		web = RestrictedWebViewWidget(url="https://addons-ecs.forgesvc.net/api/v2/addon/" + str(id) + "/description")
		web.show()
		sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    web = RestrictedWebViewWidget(url="https://addons-ecs.forgesvc.net/api/v2/addon/311054/description")
    web.show()
    sys.exit(app.exec_())