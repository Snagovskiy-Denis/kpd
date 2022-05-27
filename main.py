import logging
logging.basicConfig(level=logging.DEBUG)
logging.info('Initialize module')


import sys
import django
logging.debug(sys.version_info)
logging.debug('Django version - %s', django.get_version())



#=========== django backend ========
from django.conf import settings
from django.urls import path
from django.http import HttpResponse


logging.debug('django imports done')


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
from kivy.lang import Builder
from requests import get, ConnectionError


def build_url(host: str, port: int) -> str:
    return ':'.join((host, str(port)))


def runserver(host: str, port: int) -> None:
    from django.core.management import execute_from_command_line
    logging.info('Starting server at %s:%s', host, port)
    execute_from_command_line([__name__, 'runserver', '--noreload', build_url(host, port)])


def request_server(host: str, port: int) -> str:
    url = build_url(host, port)
    logging.info('GET %s', url)
    try:
        return 'Response: ' + get('http://' + url).text
    except ConnectionError:
        logging.error('ConnectionError')
        return 'Server is down!'
    except Exception as e:
        logging.error('%s', e)
        return 'Unexpected error!'


class ServerBox(BoxLayout):
    host = '.'.join('0' * 4)
    port = 8080

    def runserver(self):
        Process(target=runserver, args=(self.host, self.port)).start()
        self.response_label.text = 'Start server...'

    def request_server(self):
        self.response_label.text = request_server(self.host, self.port)


class MyApp(App):
    def build(self):
        return ServerBox()


if __name__ == '__main__':
    Builder.load_string('''
<ServerBox>:
    orientation: 'vertical'

    but_1: but_1
    but_2: but_2
    response_label: lab_1

    Button:
        id: but_1
        font_size: 20
        text: 'Start server'
        on_press: root.runserver()

    Label:
        id: lab_1
        font_size: 20
        text: 'Waiting for a tap'

    Button:
        id: but_2
        font_size: 20
        text: 'GET / HTTP/1.1'
        on_press: root.request_server()
''')
    freeze_support()
    MyApp().run()
