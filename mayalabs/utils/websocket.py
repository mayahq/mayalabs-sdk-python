import asyncio
import websockets
import json
import sys
from colorama import init, Fore, Back, Style
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

# maya_log_prefix = Fore.MAGENTA + '[Maya]' + Style.RESET_ALL
maya_log_prefix = '[Maya]'

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
    
    def on(self, event, handler):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def handle_events(self, log_prefix, events):
        pass
        for event in events:
            if event['topic'] == 'nodeexecstatus':
                if (event['data']['status'] == 'running'):
                    nodeId = event['data']['nodeId']
                    print(log_prefix, Fore.CYAN + f'Running node: {nodeId}' + Style.RESET_ALL)
            
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
                nodeId = event['data']['id']
                print(log_prefix, LOG_COLOR + f'Received {logLevel} message from node {nodeId}: {content}' + Style.RESET_ALL)
            
            elif event['topic'] == 'notification/node/added':
                nodes = event['data']
                if len(nodes) == 0: return

                module_name = nodes[0]['module']
                module_version = nodes[0]['version']
                print(log_prefix, Fore.CYAN + f'Installed module {module_name}@{module_version}' + Style.RESET_ALL)
            
            # else:
            #     print('event received:', event)



                
    @authenticate
    async def start_listener(self, events=execution_events, log_prefix=maya_log_prefix, api_key=None):
        try:
            async with websockets.connect(self.url) as websocket:
                # print('Connected to worker at', self.url)
                self.websocket = websocket
                
                await websocket.send(json.dumps({ 'auth': api_key }))
                auth_response = await websocket.recv()
                # print('Auth response:', auth_response)

                for event in events:
                    # print('subscribing to', event)
                    await websocket.send(json.dumps({ 'subscribe': event }))
                while True:
                    message = await websocket.recv()
                    self.handle_events(log_prefix, json.loads(message))
                    # print('Received message from websocket:', message)
        except asyncio.CancelledError:
            await self.websocket.close()

    async def _disconnect(self, future):
        if self.websocket.open:
            await self.websocket.close()


