import logging

from ..component.action import Action
from ..payload import CommandResultPayload
from ..payload import Payload
from ..payload import ErrorPayload
from ..worker import ComponentWorker

LOG = logging.getLogger(__name__)


class ServiceWorker(ComponentWorker):
    """Service worker task class."""

    def create_component_instance(self, payload):
        return Action(
            payload.get('command/name'),
            Payload(payload.get('command/arguments/params')),
            Payload(payload.get('command/arguments/transport')),
            self.source_file,
            self.component_name,
            self.component_version,
            self.platform_version,
            debug=self.debug,
            )

    def component_to_payload(self, command_name, component):
        if not isinstance(component, Action):
            LOG.error('Invalid service %s response', self.component_name)
            payload = ErrorPayload.new()
        else:
            # TODO: New transport payload based on component data ? @JW
            payload = component.get_transport()

        # Add result payload as a full entity result
        return CommandResultPayload.new(command_name, payload.entity())
