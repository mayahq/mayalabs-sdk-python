import uuid
import asyncio
import websockets
import json
from typing import Dict, Any
from .log import log
import os
from ..mayalabs import authenticate
from ..consts import api_base_url, api_ws_url
from colorama import Fore, Style
from ..exceptions import GenerationException


def get_message(pac_message):
    pass
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

            return {
                'status': 'progress',
                'message': f'Generated step [{step_prefix}]: {step_text}'
            }
    except:
        return {
            'status': 'error',
            'message': 'Something went wrong'
        }


class PacTask:
    @authenticate
    def __init__(self, type: str, opts: Dict[str, Any], api_key=None):
        self.type = type
        self.opts = opts
        self.api_key = api_key
        self.done_future = asyncio.Future()

    async def execute(self):
        connection_id = uuid.uuid4()
        url = f"{api_ws_url}?connId={connection_id}&apiKey={self.api_key}"
        
        async with websockets.connect(url) as socket:
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

                    msg = get_message(data)

                    if msg['status'] == 'error':
                        # print('[Maya]', Fore.RED + 'There was an error during program generation: ' + msg['message'] + Style.RESET_ALL)
                        # raise GenerationException('Error occured during generation: ' + msg['message'])
                        log(
                            Fore.RED + 'There was an error during program generation: ' + msg['message'] + Style.RESET_ALL,
                            prefix='mayalabs',
                            prefix_color=Fore.BLACK
                        )
                        raise Exception('Error occured during generation: ' + msg['message'])
                    elif msg['status'] == 'success':
                        break
                    else:
                        log(
                            Fore.CYAN + msg['message'] + Style.RESET_ALL,
                            prefix='mayalabs',
                            prefix_color=Fore.BLACK
                        )
                    
                    # self.done_future.set_result(data)

    async def done(self):
        await self.done_future


class GenerateTask(PacTask):
    def __init__(self, session_id: str):
        super().__init__(
            type="GENERATE",
            opts={"session_id": session_id},
        )


class InstructTask(PacTask):
    def __init__(self, session_id: str, instruction: str, from_scratch: bool):
        super().__init__(
            type="INSTRUCT",
            opts={
                "session_id": session_id,
                "instruction": instruction,
                "from_scratch": from_scratch,
            },
        )

