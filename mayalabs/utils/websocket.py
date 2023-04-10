import asyncio
import websockets
import json
from colorama import init, Fore, Style
from .log import log
from ..mayalabs import authenticate
from .defaults import default_log_level

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

class WebsocketListener:
    def __init__(self, url):
        pass
        self.url = url
        self.handlers = {}
        self.websocket = None
        self.current_prefix = ''
    
    def on(self, event, handler):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def handle_events(self, log_prefix, prefix_color, events, node_step_map={}):
        for event in events:
            if (not isinstance(event, dict)) or ('topic' not in event):
                return
            
            if event['topic'] == 'nodeexecstatus':
                # print('event', json.dumps(event))
                if (event['data']['status'] == 'running'):
                    nodeId = event['data']['nodeId']

                    step = node_step_map.get(nodeId, None)
                    if step is None: continue
                    if step['prefix'] == self.current_prefix: continue

                    prefix = step['prefix']
                    content = step['content']

                    self.current_prefix = prefix
                    log(
                        Fore.CYAN + f'Running step {prefix.strip()} {content}' + Style.RESET_ALL,
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
    async def start_listener(
        self, 
        events=execution_events, 
        log_prefix=maya_log_prefix, 
        api_key=None, 
        prefix_color=Fore.WHITE,
        session = None,
        on_connect: asyncio.Event = None
    ):
        node_step_map = {}
        if session:
            steps = session.steps
            stitched_flow = session.stitched_flow

            for node in stitched_flow:
                id = node.get('id', None)
                step_id = node.get('_step_id', None)

                if not id or not step_id: continue

                node_step_map[id] = {
                    'prefix': steps[step_id]['prefix'],
                    'content': steps[step_id]['text']
                }

        self.current_prefix = ''

        try:
            async with websockets.connect(self.url) as websocket:
                self.websocket = websocket
                await websocket.send(json.dumps({ 'auth': api_key }))
                await websocket.recv()

                if on_connect: on_connect.set()

                while True:
                    message = await websocket.recv()
                    self.handle_events(log_prefix, prefix_color, json.loads(message), node_step_map=node_step_map)


        except asyncio.CancelledError:
            if self.websocket and self.websocket.open:
                await self.websocket.close()
        except websockets.exceptions.ConnectionClosedError:
            log(Fore.RED + 'Connection closed unexpectedly by Function', prefix=log_prefix, prefix_color=prefix_color)
            raise Exception('Connection closed unexpectedly by Function')

    async def _disconnect(self, future):
        if self.websocket.open:
            await self.websocket.close()


