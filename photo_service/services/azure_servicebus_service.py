"""Moduel for Azure Service Bus Service."""
import json
import logging
import os
from typing import Any

from aiohttp.web_exceptions import HTTPUnprocessableEntity
from azure.servicebus.aio import ServiceBusClient

from photo_service.adapters import VideoEventsAdapter
from photo_service.models.video_event_model import VideoEvent

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
    async def receive_messages(cls: Any, db: Any) -> list:
        """Receive messages from Azure Service Bus - return list of message ids."""
        message_id_list = []
        # create a Service Bus client using the connection string
        async with ServiceBusClient.from_connection_string(
            conn_str=NAMESPACE_CONNECTION_STR, logging_enable=False
        ) as servicebus_client:
            async with servicebus_client:
                # get the Queue Receiver object for the queue
                receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
                async with receiver:
                    received_msgs = await receiver.receive_messages(
                        max_wait_time=5, max_message_count=20
                    )
                    for message in received_msgs:
                        logging.debug(f"Received message: {message}")
                        # store message in database - create video_event, id from remote id
                        try:
                            message_dict = json.loads(str(message))
                            message_dict["id"] = str(message.message_id)
                            video_event = VideoEvent.from_dict(message_dict)

                            # insert new video_event
                            result = await VideoEventsAdapter.create_video_event(
                                db, video_event.to_dict()
                            )
                            logging.debug(f"Inserted video_event with id: {id}")
                            if result:
                                message_id_list.append(id)
                                # complete the message so that the message is removed from the queue
                                await receiver.complete_message(message)
                        except KeyError as e:
                            raise HTTPUnprocessableEntity(
                                reason=f"Mandatory property {e.args[0]} is missing."
                            ) from e

                        logging.debug("End for message async")
        return message_id_list
