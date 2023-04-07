import uuid
import asyncio
import websockets
import json
from typing import Dict, Any
from .log import log
import os
from ..mayalabs import authenticate
from .defaults import default_api_ws_url, default_log_level
from colorama import Fore, Style
from ..exceptions import GenerationException
import traceback


def get_message(pac_message):
    try:
        if pac_message['status'] and pac_message['status'] == 'complete':
            return {
                'status': 'success',
                'message': 'Generation successful'
            }
        elif 'error' in pac_message and pac_message['error'] == True:
            msg = pac_message['msg']
            if not msg:
                msg = 'Something went wrong'
            return {
                'status': 'error',
                'message': msg
            }
        elif 'metadata' in pac_message and 'steps' in pac_message:
            generated_step_id = pac_message['metadata']['generated_step_id']
            generated_step = pac_message['steps'][generated_step_id]

            step_prefix = generated_step['prefix']
            step_text = generated_step['text']
            if step_prefix[-1] == '.':
                step_prefix = step_prefix[:-1]

            if generated_step.get('error', False):
                return {
                    'status': 'error',
                    'message': f'Could not generate step [{step_prefix}] ({step_text})'
                }

            return {
                'status': 'progress',
                'message': f'Generated step [{step_prefix}]: {step_text}'
            }
    except Exception as e:
        traceback.print_exc()
        return {
            'status': 'error',
            'message': 'Something went wrong'
        }

def get_generation_id(pac_message):
    try:
        if pac_message['status'] and pac_message['status'] == 'complete':
            return {
                'status': 'success',
                'message': 'Generation successful'
            }
        elif 'error' in pac_message and pac_message['error'] == True:
            msg = pac_message['msg']
            if not msg:
                msg = 'Something went wrong'
            return {
                'status': 'error',
                'message': msg
            }
        elif 'metadata' in pac_message and 'steps' in pac_message:
            generated_step_id = pac_message['metadata']['generated_step_id']
            generated_step = pac_message['steps'][generated_step_id]
            session_id = pac_message['session_id']
            step_id = pac_message['metadata'].get('generated_step_id', "")
            step_prefix = generated_step['prefix']
            generation_id = generated_step['generation_id']
            generation_error = generated_step['error']
            step_text = generated_step['text']
            if step_prefix[-1] == '.':
                step_prefix = step_prefix[:-1]

            if generated_step.get('error', False):
                if default_log_level() == "debug":
                    return {
                        'status': 'error',
                        'message': f'Could not generate step [{session_id}][{step_id}]-[{step_prefix}] ({step_text + generation_error})'
                    }
                elif default_log_level() == "info":
                    return {
                        'status': 'error',
                        'message': f'Could not generate step [{step_prefix}] ({step_text})'
                    }

            if default_log_level() == "debug":
                return {
                    'status': 'progress',
                    'message': f'Generated step [{session_id}][{step_id}]-[{step_prefix}]: {step_text}'
                }
            else:
                return {
                    'status': 'progress',
                    'message': f'Generated step [{step_prefix}]: {step_text}'
                }
    except Exception as e:
        traceback.print_exc()
        return {
            'status': 'error',
            'message': 'Something went wrong'
        }

async def empty_function(placeholder):
    return 1   


class PacTask:
    @authenticate
    def __init__(self, type: str, opts: Dict[str, Any], api_key=None):
        self.type = type
        self.opts = opts
        self.api_key = api_key
        self.done_future = asyncio.Future()
        self.handlers = []
        self.websocket = None
        self.handle_message = empty_function

    def on_message(self, handler):
        self.handlers.append(handler)
        pass

    async def execute(self):
        try:
            connection_id = uuid.uuid4()
            api_ws_url = default_api_ws_url()
            url = f"{api_ws_url}?connId={connection_id}&apiKey={self.api_key}"
            
            async with websockets.connect(url) as socket:
                self.websocket = socket
                task_id = uuid.uuid4()

                message = {
                    "task_id": str(task_id),
                    "type": self.type,
                    "data": self.opts,
                }
                await socket.send(json.dumps(message))

                async for message in socket:
                    msg_object = json.loads(json.loads(message))
                    if msg_object["task_id"] == str(task_id):
                        data = msg_object["data"]
                        if isinstance(data, str):
                            data = json.loads(data)

                        for handler in self.handlers:
                            handler(data, self)
                        await self.handle_message(data)

                        msg = None
                        if self.type == "GENERATE":
                            msg = get_generation_id(data)
                        elif self.type == 'TALK':
                            pass

                        if msg is None:
                            continue
                        if msg['status'] == 'error':
                            # print('[Maya]', Fore.RED + 'There was an error during program generation: ' + msg['message'] + Style.RESET_ALL)
                            # raise GenerationException('Error occured during generation: ' + msg['message'])
                            log(
                                Fore.RED + 'Error during program generation: ' + msg['message'] + Style.RESET_ALL,
                                prefix='mayalabs',
                                prefix_color=Fore.BLACK
                            )
                        elif msg['status'] == 'success':
                            break
                        else:
                            log(
                                Fore.CYAN + msg['message'] + Style.RESET_ALL,
                                prefix='mayalabs',
                                prefix_color=Fore.BLACK
                            )
                            # print('received', data)
                    
        except asyncio.CancelledError:
            self.websocket.close()
            pass

    async def done(self):
        await self.done_future


class GenerateTask(PacTask):
    def __init__(self, session_id: str):
        super().__init__(
            type="GENERATE",            opts={
            "session_id": session_id,
            "repositories": []
            },
        )


class InstructTask(PacTask):
    def __init__(self, session_id: str, instruction: str, from_scratch: bool):
        super().__init__(
            type="TALK",
            opts={
                "session_id": session_id,
                "instruction": instruction,
                "from_scratch": from_scratch,
                "repositories": []
            },
        )
        async def handle_message(message):
            if message['metadata']['status'] == 'complete':
                await self.websocket.close()
                return

        self.handle_message = handle_message
