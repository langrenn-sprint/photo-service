"""Resource module for service instances resources."""

import json
import logging
import os

from aiohttp import hdrs
from aiohttp.web import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPUnprocessableEntity,
    Response,
    View,
)
from dotenv import load_dotenv
from multidict import MultiDict

from photo_service.adapters import UsersAdapter
from photo_service.models import ServiceInstance
from photo_service.services import (
    IllegalValueError,
    ServiceInstanceNotFoundError,
    ServiceInstancesService,
)
from photo_service.utils.jwt_utils import extract_token_from_request

load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "8080")
BASE_URL = f"http://{HOST_SERVER}:{HOST_PORT}"


class ServiceInstancesView(View):
    """Class representing service instances resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]
        if "eventId" in self.request.rel_url.query:
            event_id = self.request.rel_url.query["eventId"]
        else:
            event_id = ""

        if "serviceType" in self.request.rel_url.query:
            service_type = self.request.rel_url.query["serviceType"]
            service_instances = (
                await ServiceInstancesService.get_service_instances_by_service_type(
                    db, event_id, service_type
                )
            )
        elif "status" in self.request.rel_url.query:
            status = self.request.rel_url.query["status"]
            service_instances = (
                await ServiceInstancesService.get_service_instances_by_status(
                    db, event_id, status
                )
            )
        else:
            service_instances = await ServiceInstancesService.get_all_service_instances(
                db, event_id
            )
        _list = [_e.to_dict() for _e in service_instances]
        body = json.dumps(_list, default=str, ensure_ascii=False)
        return Response(status=200, body=body, content_type="application/json")

    async def post(self) -> Response:
        """Post route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        logging.debug(
            f"Got create request for service instance {body} of type {type(body)}"
        )
        try:
            service_instance = ServiceInstance.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            service_instance_id = await ServiceInstancesService.create_service_instance(
                db, service_instance
            )
        except IllegalValueError as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        if service_instance_id:
            logging.debug(
                f"inserted document with service_instance_id {service_instance_id}"
            )
            headers = MultiDict(
                [
                    (
                        hdrs.LOCATION,
                        f"{BASE_URL}/service-instances/{service_instance_id}",
                    )
                ]
            )

            return Response(status=201, headers=headers)
        raise HTTPBadRequest from None


class ServiceInstanceView(View):
    """Class representing a single service instance resource."""

    async def get(self) -> Response:
        """Get route function."""
        db = self.request.app["db"]

        service_instance_id = self.request.match_info["serviceInstanceId"]
        logging.debug(f"Got get request for service instance {service_instance_id}")

        try:
            service_instance = await ServiceInstancesService.get_service_instance_by_id(
                db, service_instance_id
            )
        except ServiceInstanceNotFoundError as e:
            raise HTTPNotFound(reason=str(e)) from e
        logging.debug(f"Got service instance: {service_instance}")
        body = service_instance.to_json()
        return Response(status=200, body=body, content_type="application/json")

    async def put(self) -> Response:
        """Put route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        body = await self.request.json()
        service_instance_id = self.request.match_info["serviceInstanceId"]
        logging.debug(
            f"Got request-body {body} for {service_instance_id} of type {type(body)}"
        )
        logging.debug(
            f"Got put request for service instance {body} of type {type(body)}"
        )
        try:
            service_instance = ServiceInstance.from_dict(body)
        except KeyError as e:
            raise HTTPUnprocessableEntity(
                reason=f"Mandatory property {e.args[0]} is missing."
            ) from e

        try:
            await ServiceInstancesService.update_service_instance(
                db, service_instance_id, service_instance
            )
        except IllegalValueError as e:
            raise HTTPUnprocessableEntity(reason=str(e)) from e
        except ServiceInstanceNotFoundError as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)

    async def delete(self) -> Response:
        """Delete route function."""
        db = self.request.app["db"]
        token = extract_token_from_request(self.request)
        try:
            await UsersAdapter.authorize(token, roles=["admin", "photo-admin"])
        except Exception as e:
            raise e from e

        service_instance_id = self.request.match_info["serviceInstanceId"]
        logging.debug(f"Got delete request for service instance {service_instance_id}")

        try:
            await ServiceInstancesService.delete_service_instance(
                db, service_instance_id
            )
        except ServiceInstanceNotFoundError as e:
            raise HTTPNotFound(reason=str(e)) from e
        return Response(status=204)
