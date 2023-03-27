import uuid
import asyncio
import websockets
import json
from typing import Dict, Any
import os
from ..mayalabs import authenticate
from ..consts import api_base_url, api_ws_url


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
            print(f"TaskID: {task_id}")

            message = {
                "task_id": str(task_id),
                "type": self.type,
                "data": self.opts,
            }
            await socket.send(json.dumps(message))

            async for message in socket:
                msg_object = json.loads(json.loads(message))
                print(f"Received from websocket: {msg_object}")
                if msg_object["task_id"] == str(task_id):
                    data = msg_object["data"]
                    if isinstance(data, str):
                        data = json.loads(data)
                    self.done_future.set_result(data)
                    break

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

