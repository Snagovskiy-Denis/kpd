#=========== django backend ========
from django.conf import settings
from django.urls import path
from django.http import HttpResponse


settings.configure(
    DEBUG=True,
    SECRET_KEY='iloveyou',
    ROOT_URLCONF=__name__,
)


urlpatterns = [path('', lambda request: HttpResponse('Hello, World!'))]


#========== kivy frontend =========================
from multiprocessing import Process, freeze_support
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock

from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
else:
    if settings.DEBUG is False:
        raise NotImplementedError('Supports Android platform only')
    run_on_ui_thread = lambda function: function
    WebView = None
    WebViewClient = None
    activity = None


HOST = '.'.join('0' * 4)
PORT = 8080

URL = ':'.join((HOST, str(PORT)))
SCHEMA = 'http://'


def create_server(host: str, port: int) -> None:
    from django.core.management import execute_from_command_line
    execute_from_command_line([__name__, 'runserver', '--noreload', URL])


@run_on_ui_thread
def create_webview(*args):
    webview = WebView(activity)
    webview.getSettings().setJavaScriptEnabled(True)
    wvc = WebViewClient()
    webview.setWebViewClient(wvc)
    activity.setContentView(webview)
    webview.loadUrl(SCHEMA + URL)


class WebviewWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(create_webview, 0)


class ServiceApp(App):
    def build(self):
        Process(target=create_server, args=(HOST, PORT)).start()
        return WebviewWidget()


if __name__ == '__main__':
    freeze_support()
    ServiceApp().run()
