import asyncio
import websockets
import json
import sys
from colorama import init, Fore, Back, Style
from .log import log
from ..mayalabs import authenticate

init()

execution_events = [
    'debug',
    'status/#',
    'mayanodeerror',
    'mayanodewarning',
    'nodeexecstatus'
]

deploy_events = [
    'notification/runtime-deploy',
    'notification/#',
    'notification/node/#',
    # 'event-log/#'
]

maya_log_prefix = 'mayalabs'

def rewrite_last_log_line(text):
    sys.stdout.write('\r')
    print(text)

def add_line_to_log(text):
    last_line = sys.stdout.readlines()[-1]
    sys.stdout.write('\r')


class WebsocketListener:
    def __init__(self, url):
        pass
        self.url = url
        self.handlers = {}
        self.websocket = None
    
    def on(self, event, handler):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def handle_events(self, log_prefix, prefix_color, events):
        for event in events:
            if (not isinstance(event, dict)) or ('topic' not in event):
                return
            
            if event['topic'] == 'nodeexecstatus':
                if (event['data']['status'] == 'running'):
                    nodeId = event['data']['nodeId']
                    log(
                        Fore.CYAN + f'Running node: {nodeId}' + Style.RESET_ALL,
                        prefix=log_prefix,
                        prefix_color=prefix_color
                    )
            
            elif event['topic'] == 'debug':
                msg_format = event['data']['format']
                content = event['data']['msg']

                level = event['data'].get('level', None)
                
                LOG_COLOR = Fore.YELLOW
                logLevel = 'debug'
                if level == 20:
                    LOG_COLOR = Fore.RED
                    logLevel = 'error'


                if msg_format == 'Object':
                    content = json.loads(content)
                try:
                    nodeId = event['data']['id']
                    log(
                        LOG_COLOR + f'Received {logLevel} message from node {nodeId}: {content}' + Style.RESET_ALL, 
                        prefix=log_prefix,
                        prefix_color=prefix_color
                    )
                except Exception as err:
                    log(
                        LOG_COLOR + f'Received {logLevel} : {content}' + Style.RESET_ALL, 
                        prefix=log_prefix,
                        prefix_color=prefix_color
                    )
            
            elif event['topic'] == 'notification/node/added':
                nodes = event['data']
                if len(nodes) == 0: return

                module_name = nodes[0]['module']
                module_version = nodes[0]['version']
                log(
                    Fore.CYAN + f'Installed module {module_name}@{module_version}' + Style.RESET_ALL, 
                    prefix=log_prefix,
                    prefix_color=prefix_color
                )



                
    @authenticate
    async def start_listener(self, events=execution_events, log_prefix=maya_log_prefix, api_key=None, prefix_color=Fore.WHITE):
        try:
            async with websockets.connect(self.url) as websocket:
                self.websocket = websocket
                await websocket.send(json.dumps({ 'auth': api_key }))
                await websocket.recv()

                for event in events:
                    await websocket.send(json.dumps({ 'subscribe': event }))
                while True:
                    message = await websocket.recv()
                    self.handle_events(log_prefix, prefix_color, json.loads(message))
        except asyncio.CancelledError:
            await self.websocket.close()
        except websockets.exceptions.ConnectionClosedError:
            log(Fore.RED + 'Connection closed unexpectedly by Function', prefix=log_prefix, prefix_color=prefix_color)
            raise Exception('Connection closed unexpectedly by Function')

    async def _disconnect(self, future):
        if self.websocket.open:
            await self.websocket.close()


