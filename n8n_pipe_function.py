"""
title: n8n Pipe Function
article: https://www.pondhouse-data.com/blog/integrating-n8n-with-open-webui
version: 0.2.0

This module defines a Pipe class that utilizes an N8N workflow for an Agent
n8n webhook URL: http://n8n:5678/webhook-test/[your webhook URL]
"""

from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import os
import time
import aiohttp
import asyncio


class Pipe:
    class Valves(BaseModel):
        n8n_url: str = Field(
            default="http://n8n:5678/webhook-test/[your webhook URL]"
        )
        n8n_bearer_token: str = Field(default="...")
        input_field: str = Field(default="chatInput")
        response_field: str = Field(default="output")
        emit_interval: float = Field(
            default=2.0, description="Interval in seconds between status emissions"
        )
        enable_status_indicator: bool = Field(
            default=True, description="Enable or disable status indicator emissions"
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "n8n_pipe"
        self.name = "N8N Pipe"
        self.valves = self.Valves()
        self.last_emit_time = 0

    async def emit_status(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        level: str,
        message: str,
        done: bool,
    ):
        current_time = time.time()
        if (
            __event_emitter__
            and self.valves.enable_status_indicator
            and (
                current_time - self.last_emit_time >= self.valves.emit_interval or done
            )
        ):
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "status": "complete" if done else "in_progress",
                        "level": level,
                        "description": message,
                        "done": done,
                    },
                }
            )
            self.last_emit_time = current_time

    async def make_n8n_request(self, payload: dict) -> dict:
        """Separate async function to handle the N8N API request"""
        headers = {
            "Authorization": f"Bearer {self.valves.n8n_bearer_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.valves.n8n_url, json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data[self.valves.response_field]
                else:
                    error_text = await response.text()
                    raise Exception(f"Error: {response.status} - {error_text}")

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __metadata__: Optional[dict] = None,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        __event_call__: Callable[[dict], Awaitable[dict]] = None,
    ) -> Optional[dict]:
        n8n_response = None

        try:
            await self.emit_status(
                __event_emitter__, "info", "Calling N8N Workflow...", False
            )

            messages = body.get("messages", [])

            # Verify a message is available
            if messages:
                question = messages[-1]["content"]
                if "Prompt: " in question:
                    question = question.split("Prompt: ")[-1]

                await self.emit_status(
                    __event_emitter__, "info", "Processing request...", False
                )

                # Prepare payload
                payload = {"sessionId": __metadata__["chat_id"]}
                payload[self.valves.input_field] = question
                payload["user"] = __user__

                # Make the API request
                n8n_response = await self.make_n8n_request(payload)

                # Set assistant message with chain reply
                body["messages"].append({"role": "assistant", "content": n8n_response})

                await self.emit_status(
                    __event_emitter__, "info", "Processing response...", False
                )

            else:
                await self.emit_status(
                    __event_emitter__,
                    "error",
                    "No messages found in the request body",
                    True,
                )
                body["messages"].append(
                    {
                        "role": "assistant",
                        "content": "No messages found in the request body",
                    }
                )
                return "No messages found in the request body"

        except Exception as e:
            error_message = f"Error: {str(e)}"
            await self.emit_status(
                __event_emitter__,
                "error",
                error_message,
                True,
            )
            body["messages"].append({"role": "assistant", "content": error_message})
            return {"error": error_message}

        finally:
            await self.emit_status(__event_emitter__, "info", "Complete", True)

        return n8n_response
