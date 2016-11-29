import jsonschema

from katana.errors import KatanaError


class DataValidationError(KatanaError):
    """Transport data validation error class."""


def traverse_to_initial_error(err, path=''):
    """Get initial error object from error context.

    Error is saved under context when a validation error happens
    inside a sub schema.

    :rtype: `jsonschema.exceptions.ValidationError`

    """

    path = path + '/'.join(str(item) for item in err.path)
    if err.context:
        # Keep getting error from context as long and a context exists
        return traverse_to_initial_error(err.context[0], path)

    return (err, path)


def define_schema_objects(schema, entity_definition):
    """Define JSON schema object properties using an entity definition.

    :param schema: JSON schema object.
    :type schema: dict
    :param entity_definition: Action entity definition.
    :type entity_definition: dict

    """

    properties = schema['properties']
    for entity in entity_definition:
        if not entity.get('optional', False):
            schema['required'].append(entity['name'])

        obj_schema = properties[entity['name']] = {
            'type': 'object',
            'properties': {},
            'required': [],
            'additionalProperties': False,
            }

        if 'field' in entity:
            define_schema_properties(obj_schema, entity['field'])

        if 'fields' in entity:
            define_schema_objects(obj_schema, entity['fields'])


def define_schema_properties(schema, entity_definition):
    """Define JSON schema simple and object properties using an entity definition.

    :param schema: JSON schema object.
    :type schema: dict
    :param entity_definition: Action entity definition.
    :type entity_definition: dict

    """

    properties = schema['properties']
    for entity in entity_definition:
        if 'fields' in entity:
            define_schema_objects(schema, entity['fields'])
            if not entity.get('optional', False):
                schema['required'].append(entity['name'])
        else:
            properties[entity['name']] = {'type': entity.get('type', 'string')}
            if not entity.get('optional', False):
                schema['required'].append(entity['name'])


def entity_to_jsonschema(entity):
    """Create a JSON schema to validate an entity definition.

    :param entity: Action entity definition.
    :type entity: dict

    :returns: A JSON schema object.
    :rtype: dict

    """

    # Create the base JSON schema
    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {},
        'required': [],
        'additionalProperties': False,
        }

    # Add first level properties
    if 'field' in entity:
        define_schema_properties(schema, entity['field'])

    # Add first level objects
    if 'fields' in entity:
        define_schema_objects(schema, entity['fields'])

    return schema


def validate_entity(obj, entity):
    """Check that an entity object is valid for an entity definition.

    :param obj: Entity object to validate.
    :type obj: dict
    :param entity: Action entity definition.
    :type entity: dict

    """

    try:
        jsonschema.validate(obj, entity_to_jsonschema(entity))
    except jsonschema.exceptions.ValidationError as err:
        err, path = traverse_to_initial_error(err)

        if path:
            message = 'Entity field "{}" validation failed: {}'.format(
                path,
                err.message,
                )
        else:
            message = 'Entity validation failed: {}'.format(err.message)

        raise DataValidationError(message)


def validate_collection(collection, entity):
    """Check that all entities in a collection are valid for an entity definition.

    :param collection: Collection of entity objects to validate.
    :type collection: list
    :param entity: Action entity definition.
    :type entity: dict

    """

    try:
        jsonschema.validate(collection, {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': entity_to_jsonschema(entity),
            })
    except jsonschema.exceptions.ValidationError as err:
        err, path = traverse_to_initial_error(err)

        if path:
            message = 'Collection item {} validation failed: {}'.format(
                path,
                err.message,
                )
        else:
            message = 'Collection validation failed: {}'.format(err.message)

        raise DataValidationError(message)
