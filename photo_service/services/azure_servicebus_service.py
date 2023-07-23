"""Moduel for Azure Service Bus Service."""
import logging
import os
from typing import Any

from azure.servicebus.aio import ServiceBusClient

NAMESPACE_CONNECTION_STR = os.getenv("SERVICEBUS_NAMESPACE_CONNECTION_STR", "")
QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "")


class AzureServiceBusService:
    """Class for Azure Service Bus Service."""

    @classmethod
    async def send_message(cls: Any, message: str) -> None:
        """Send message to Azure Service Bus."""
        async with ServiceBusClient.from_connection_string(
            conn_str=NAMESPACE_CONNECTION_STR, logging_enable=True
        ) as client:
            async with client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
                await sender.send_messages(message)
                logging.debug(f"Sent message: {message}")
        return None

    @classmethod
    async def receive_message(cls: Any) -> str:
        """Receive message from Azure Service Bus."""
        async with ServiceBusClient.from_connection_string(
            conn_str=NAMESPACE_CONNECTION_STR, logging_enable=True
        ) as client:
            async with client.get_queue_receiver(queue_name=QUEUE_NAME) as receiver:
                async for message in receiver:
                    logging.debug(f"Received message: {message}")
                    await message.complete()
                    return message
        return ""
