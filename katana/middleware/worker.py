"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import logging

from ..api.request import Request
from ..api.response import Response
from ..api.transport import Transport
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
            query=MultiDict(payload.get('request/query', {})),
            headers=MultiDict(payload.get('request/headers', {})),
            post_data=MultiDict(payload.get('request/post_data', {})),
            body=payload.get('request/body'),
            files=MultiDict(payload.get('request/files', {})),
            service_name=payload.get('call/service'),
            service_version=payload.get('call/version'),
            action_name=payload.get('call/action'),
            debug=self.debug,
            )

    def _create_response_component_instance(self, payload):
        code, text = payload.get('response/status').split(' ', 1)
        return Response(
            int(code),
            text,
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
        payload = Payload(payload.get('command/arguments'))
        if middleware_type == 'request':
            return self._create_request_component_instance(payload)
        elif middleware_type == 'response':
            return self._create_response_component_instance(payload)
        else:
            LOG.error('Unknown Middleware type: "%s"', middleware_type)
            return ErrorPayload.new().entity()

    def component_to_payload(self, payload, component):
        """Convert component to a command result payload.

        Valid components are `Request` and `Response` objects.

        :params payload: Command payload from current request.
        :type payload: `CommandPayload`
        :params component: The component being used.
        :type component: `Component`

        :returns: A result payload.
        :rtype: `Payload`

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
                headers=dict(component.get_headers()),
                )
        else:
            LOG.error('Invalid Middleware callback result')
            payload = ErrorPayload.new()

        return payload.entity()

    def create_error_payload(self, exc, component, **kwargs):
        # Create a response with the error
        return ResponsePayload.new(
            version=component.get_protocol_version(),
            status='500 Internal Server Error',
            body=str(exc),
            ).entity()
