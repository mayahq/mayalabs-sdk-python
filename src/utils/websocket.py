import asyncio
import websockets
import json
import sys
from colorama import init, Fore, Back, Style

init()

execution_events = [
    'debug',
    'status/#',
    'mayanodeerror',
    'mayanodewarning',
    'nodeexecstatus'
]

temp_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImY1OTNkMzYwNCJ9.eyJhdWQiOiIzMzI3MmJlOS1kOWQwLTQxNTEtODJiMy0yYmM3MjRlMDllNjgiLCJleHAiOjE2ODIyNDg0NDEsImlhdCI6MTY3OTY1NjQ0MSwiaXNzIjoibWF5YWxhYnMuaW8iLCJzdWIiOiIzMjM4YmM1Yy1kMjZhLTRmZjQtYjZjNS1lMmNjNTE4ZDMxMmMiLCJqdGkiOiI4MTdkMzU0MS0xZmYyLTQ5MGItYjlhMS00ZWE4MTRmMTYwY2MiLCJhdXRoZW50aWNhdGlvblR5cGUiOiJHT09HTEUiLCJlbWFpbCI6ImR1c2h5YW50OTMwOUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXBwbGljYXRpb25JZCI6IjMzMjcyYmU5LWQ5ZDAtNDE1MS04MmIzLTJiYzcyNGUwOWU2OCIsInJvbGVzIjpbXSwiYXV0aF90aW1lIjoxNjc5NjU2NDQxLCJ0aWQiOiI2MWUxNDQyMS03NDJlLWQxZGUtNDMzOC1hMDM5OWEzYzA4MzQiLCJwcm9maWxlU2x1ZyI6IjMyMzhiYzVjLWQyNmEtNGZmNC1iNmM1LWUyY2M1MThkMzEyYyIsImFjY2VzcyI6W3siZXhwIjo5OTk5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6IkFETUlOIiwic2x1ZyI6IjMyMzhiYzVjLWQyNmEtNGZmNC1iNmM1LWUyY2M1MThkMzEyYyIsInRpZXIiOiJQUkVNSVVNIiwidHJpYWxEYXlzIjoxNX0seyJleHAiOjk5OTk5OTk5OTk5OTksInBlcm1pc3Npb25zIjoiQURNSU4iLCJzbHVnIjoibWF5YWhxIiwidGllciI6IlBSRU1JVU0iLCJ0cmlhbERheXMiOjE1fSx7ImV4cCI6OTk5OTk5OTk5OTk5OSwicGVybWlzc2lvbnMiOiJBRE1JTiIsInNsdWciOiJheWFtIiwidGllciI6IkZSRUUiLCJ0cmlhbERheXMiOjE0fSx7ImV4cCI6OTk5OTk5OTk5OTk5OSwicGVybWlzc2lvbnMiOiJBRE1JTiIsInNsdWciOiJheWFtMiIsInRpZXIiOiJGUkVFIiwidHJpYWxEYXlzIjoxNH0seyJleHAiOjk5OTk5OTk5OTk5OTksInBlcm1pc3Npb25zIjoiQURNSU4iLCJzbHVnIjoiYXlhbTMiLCJ0aWVyIjoiRlJFRSIsInRyaWFsRGF5cyI6MTR9LHsiZXhwIjo5OTk5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6IkFETUlOIiwic2x1ZyI6ImF5YW00IiwidGllciI6IkZSRUUiLCJ0cmlhbERheXMiOjE0fSx7ImV4cCI6OTk5OTk5OTk5OTk5OSwicGVybWlzc2lvbnMiOiJBRE1JTiIsInNsdWciOiJheWFtNSIsInRpZXIiOiJGUkVFIiwidHJpYWxEYXlzIjoxNH0seyJleHAiOjk5OTk5OTk5OTk5OTksInBlcm1pc3Npb25zIjoiQURNSU4iLCJzbHVnIjoiYXlhbTYiLCJ0aWVyIjoiRlJFRSIsInRyaWFsRGF5cyI6MTR9LHsiZXhwIjo5OTk5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6IkFETUlOIiwic2x1ZyI6ImJyYWgiLCJ0aWVyIjoiRlJFRSIsInRyaWFsRGF5cyI6MTR9LHsiZXhwIjo5OTk5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6IkFETUlOIiwic2x1ZyI6IjM3IiwidGllciI6IkZSRUUiLCJ0cmlhbERheXMiOjE0fV0sImhhc0FjY2VzcyI6InllcyJ9.lMln2YMEAwfcht4GodipN4iFydCcB7ts_0rIhgAz7bY'

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

    def handle_events(self, events):
        pass
        for event in events:
            if event['topic'] == 'nodeexecstatus':
                if (event['data']['status'] == 'running'):
                    nodeId = event['data']['nodeId']
                    print(Fore.CYAN + f'Running node: {nodeId}' + Style.RESET_ALL)
                
    
    async def start_listener(self, events=execution_events):
        try:
            async with websockets.connect(self.url) as websocket:
                # print('Connected to worker at', self.url)
                self.websocket = websocket
                
                await websocket.send(json.dumps({ 'auth': temp_key }))
                auth_response = await websocket.recv()
                # print('Auth response:', auth_response)

                for event in events:
                    # print('subscribing to', event)
                    await websocket.send(json.dumps({ 'subscribe': event }))
                while True:
                    message = await websocket.recv()
                    self.handle_events(json.loads(message))
                    # print('Received message from websocket:', message)
        except asyncio.CancelledError:
            await self.websocket.close()

    async def _disconnect(self, future):
        if self.websocket.open:
            await self.websocket.close()


