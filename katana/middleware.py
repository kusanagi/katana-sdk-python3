"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

import logging

from .api.param import param_to_payload
from .api.request import Request
from .api.response import NO_RETURN_VALUE
from .api.response import Response
from .api.transport import Transport
from .payload import ErrorPayload
from .payload import Payload
from .payload import ResponsePayload
from .payload import ServiceCallPayload
from .server import ComponentServer
from .utils import MultiDict

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

LOG = logging.getLogger(__name__)

REQUEST_MIDDLEWARE = 1
RESPONSE_MIDDLEWARE = 2
BIDIRECTIONAL_MIDDLEWARE = 3


class MiddlewareServer(ComponentServer):
    """Server class for middleware component."""

    def __init__(self, *args, **kwargs):
        from .sdk.middleware import get_component

        super().__init__(*args, **kwargs)
        self.__component = get_component()
        # Request payload attributes
        self.__attributes = {}

    @staticmethod
    def http_request_from_payload(payload):
        if not payload.path_exists('request'):
            return

        return {
            'method': payload.get('request/method'),
            'url': payload.get('request/url'),
            'protocol_version': payload.get('request/version'),
            'query': MultiDict(payload.get('request/query', {})),
            'headers': MultiDict(payload.get('request/headers', {})),
            'post_data': MultiDict(payload.get('request/post_data', {})),
            'body': payload.get('request/body'),
            'files': MultiDict(payload.get('request/files', {})),
            }

    @staticmethod
    def http_response_from_payload(payload):
        if not payload.path_exists('response'):
            return

        code, text = payload.get('response/status').split(' ', 1)
        return {
            'version': payload.get('response/version', '1.1'),
            'headers': MultiDict(payload.get('response/headers', {})),
            'status_code': int(code),
            'status_text': text,
            'body': payload.get('response/body', ''),
            }

    def _create_request_component_instance(self, payload):
        return Request(
            self.__component,
            self.source_file,
            self.component_name,
            self.component_version,
            self.framework_version,
            attributes=self.__attributes,
            variables=self.variables,
            debug=self.debug,
            # TODO: Use meta and call as arguments instead these many kwargs
            service_name=payload.get('call/service'),
            service_version=payload.get('call/version'),
            action_name=payload.get('call/action'),
            params=payload.get('call/params', []),
            rid=payload.get('meta/id'),
            timestamp=payload.get('meta/datetime'),
            gateway_protocol=payload.get('meta/protocol'),
            gateway_addresses=payload.get('meta/gateway'),
            client_address=payload.get('meta/client'),
            http_request=self.http_request_from_payload(payload),
            )

    def _create_response_component_instance(self, payload):
        return Response(
            Transport(payload.get('transport')),
            self.__component,
            self.source_file,
            self.component_name,
            self.component_version,
            self.framework_version,
            attributes=self.__attributes,
            debug=self.debug,
            variables=self.variables,
            return_value=payload.get('return', NO_RETURN_VALUE),
            # TODO: Use meta and argument
            gateway_protocol=payload.get('meta/protocol'),
            gateway_addresses=payload.get('meta/gateway'),
            http_request=self.http_request_from_payload(payload),
            http_response=self.http_response_from_payload(payload),
            )

    def create_component_instance(self, action, payload):
        """Create a component instance for current command payload.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: Command payload.
        :type payload: `CommandPayload`

        :rtype: `Request` or `Response`

        """

        payload = Payload(payload.get('command/arguments'))
        # Update request attribute values
        self.__attributes.update(payload.get('meta/attributes', {}))

        middleware_type = payload.get('meta/type')
        if middleware_type == REQUEST_MIDDLEWARE:
            return self._create_request_component_instance(payload)
        elif middleware_type == RESPONSE_MIDDLEWARE:
            return self._create_response_component_instance(payload)

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
                params=[
                    param_to_payload(param) for param in component.get_params()
                    ]
                )
        elif isinstance(component, Response):
            http_response = component.get_http_response()
            # Return a response payload
            payload = ResponsePayload.new(
                version=http_response.get_protocol_version(),
                status=http_response.get_status(),
                body=http_response.get_body(),
                headers=dict(http_response.get_headers_array()),
                )
        else:
            LOG.error('Invalid Middleware callback result')
            payload = ErrorPayload.new()

        # When attributes were setted return a payload containing
        # the attributes and the payload entity.
        if self.__attributes:
            payload = Payload(payload.entity())
            payload.set("attributes", self.__attributes)
        else:
            payload = payload.entity()

        return payload

    def create_error_payload(self, exc, component, **kwargs):
        if isinstance(component, Request):
            http = component.get_http_request()
        else:
            http = component.get_http_response()

        # Create a response with the error
        return ResponsePayload.new(
            version=http.get_protocol_version(),
            status='500 Internal Server Error',
            body=str(exc),
            ).entity()
