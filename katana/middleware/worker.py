import logging

from ..component.request import Request
from ..component.response import Response
from ..component.transport import Transport
from ..payload import CommandResultPayload
from ..payload import ErrorPayload
from ..payload import Payload
from ..payload import ResponsePayload
from ..payload import ServiceCallPayload
from ..utils import MultiDict
from ..worker import ComponentWorker

LOG = logging.getLogger(__name__)


class MiddlewareWorker(ComponentWorker):
    """Middleware worker task class."""

    def _create_request_component_instance(self, payload):
        return Request(
            payload.get('request/method'),
            payload.get('request/url'),
            self.source_file,
            self.component_name,
            self.component_version,
            self.platform_version,
            # Keyword arguments
            protocol_version=payload.get('request/version'),
            query=MultiDict(payload.get('request/query')),
            headers=MultiDict(payload.get('request/headers')),
            post_data=MultiDict(payload.get('request/post_data')),
            body=payload.get('request/body'),
            files=payload.get('request/files'),
            service_name=payload.get('call/service'),
            service_version=payload.get('call/version'),
            action_name=payload.get('call/action'),
            debug=self.debug,
            )

    def _create_response_component_instance(self, payload):
        return Response(
            payload.get('response/status', self.http_success_status),
            Transport(payload.get('transport')),
            self.source_file,
            self.component_name,
            self.component_version,
            self.platform_version,
            body=payload.get('response/body', ''),
            )

    def create_component_instance(self, payload):
        """Create a component instance for current command payload.

        :param payload: Command payload.
        :type payload: `CommandPayload`

        :rtype: `Request` or `Response`

        """

        middleware_type = payload.get('command/arguments/type')
        payload = Payload(payload.get('command/arguments/component'))
        if middleware_type == 'request':
            return self._create_request_component_instance(payload)
        elif middleware_type == 'response':
            return self._create_response_component_instance(payload)
        else:
            LOG.error('Unknown middleware command %s', middleware_type)
            # TODO: Review error w/ @JW
            return ErrorPayload.new().entity()

    def component_to_payload(self, command_name, component):
        """Convert component to a command result payload.

        Valid components are `Request` and `Response` objects.

        :params command_name: Name of command being executed.
        :type command_name: str
        :params component: The component being used.
        :type component: `Component`

        :returns: A command result payload.
        :rtype: CommandResultPayload

        """

        if isinstance(component, Request):
            # Return a service call payload
            payload = ServiceCallPayload.new(
                service=component.get_service_name(),
                version=component.get_service_version(),
                action=component.get_action_name(),
                )
        elif isinstance(component, Response):
            # Return a response payload
            payload = ResponsePayload.new(
                version=component.get_protocol_version(),
                status=component.get_status(),
                body=component.get_body(),
                headers=component.get_headers().multi_items(),
                )
        else:
            # TODO: Talk with @JW
            LOG.error('Invalid middleware %s response', self.component_name)
            payload = ErrorPayload.new()

        # Add result payload as a full entity result
        return CommandResultPayload.new(command_name, payload.entity())
