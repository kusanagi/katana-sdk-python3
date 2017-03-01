KATANA SDK for Python 3
=======================

[badges]

Python 3 SDK to interface with the **KATANA**™ framework (https://katana.kusanagi.io).

Requirements
------------

* KATANA Framework 1.0+
* Python 3.4+
* [libzmq](http://zeromq.org/intro:get-the-software) 4.1.5+

Installation
------------

Enter the following command to install the SDK in your local environment:

```
$ pip install katana-sdk-python3
```

To run all unit tests or code coverage install requirements first:

```
$ pip install -r pip-requirements.txt
```

And then run all unit test with the command:

```
$ pytest --cache-clear
```

Or, for code coverage, use the command:

```
$ pytest -q --cov=katana --cov-report=term
```

Getting Started
---------------

To start using the **KATANA SDK for Python 3** we will create a **Middleware** that handles requests and responses, and then a simple **Service**.

So first create a python module that defines a **Middleware** like this:

```python
import logging
import json

from katana.sdk import Middleware

LOG = logging.getLogger('katana')

def request_handler(request):
    return request
    
    
def response_handler(response):
    return response
    
    
if __name__ == '__main__':
    middleware = Middleware()
    middleware.request(request_handler)
    middleware.response(response_handler)
    middleware.run()
```

Save the module as `middleware-example.py`.

This module defines a **Middleware** that processes requests and also responses, so it is called two times per request.

The `request_handler` is called first, before any **Service** call, so there we have to set the **Service** name, version and action to call. To do so change the `request_handler` function to:

```python
def request_handler(request):
    http_request = request.get_http_request()
    path = http_request.get_url_path()
    LOG.info('Pre-processing request to URL %s', path)
    
    # These values would normally be extracted by parsing the URL
    request.set_service_name('users')
    request.set_service_version('0.1')
    request.set_action_name('read')
    
    return request
```

This calls the *read* action for the version *0.1* of the users **Service** for every request.

The `response_handler` is called at the end of the request/response lifecycle, after the **Service** call finishes.
For the example all responses will be JSON responses. To do so change the `response_handler` function to look like this:

```python
def response_handler(response):
    http_response = response.get_http_response()
    http_response.set_header('Content-Type', 'application/json')
    
    # Serialize transport to JSON and use it as response body
    transport = response.get_transport()
    body = json.dumps(transport.get_data())
    http_response.set_body(body)
    
    return response
```

At this point there is a complete **Middleware** defined, so the next step is to define a **Service**. Create a new python module that defines the **Service** like this:

```python
from katana.sdk import Service


def read_handler(action):
    user_id = action.get_param('id').get_value()
    
    # Users read action returns a single user entity
    action.set_entity({
        'id': user_id,
        'name': 'foobar',
        'first_name': 'Foo',
        'last_name': 'Bar',
    })
    return action
    
    
if __name__ == '__main__':
    service = Service()
    service.action('read', read_handler)
    service.run()
```

Save the module as `service-users.py`.

The final step is to define the configuration files for the example **Middleware** and **Service**.

**KATANA** configurations can be defined as *XML*, *YAML* or *JSON*.
For the examples we will use *YAML*. Create a new config file for the **Middleware** that looks like:

```yaml
"@context": urn:katana:middleware
name: example
version: "0.1"
request: true
info:
  title: Example Middleware
engine:
  runner: urn:katana:runner:python3
  path: ./middleware-example.py
```

Save the config as `middleware-example.yaml`.

And finally create a config file for the **Service** that looks like:

```yaml
"@context": urn:katana:service
name: users
version: "0.1"
http-base-path: /0.1
info:
  title: Example Users Service
engine:
  runner: urn:katana:runner:python3
  path: ./service-users.py
action:
  - name: read
    http-path: /users/{id}
    param:
      - name: id
        type: integer
        http-input: path
        required: true
```

Save the config as `service-users.yaml`.

Now you can add the **Middleware** to the **Gateway** config and run the example.

Examples
--------

*(optional) Any relevant examples to help with development*

Documentation
-------------

See the [API](https://kusanagi.io/app#katana/docs/sdk) for a technical reference of the SDK, or read the full [specification](https://kusanagi.io/app#katana/docs/sdk/specification).

For help using the framework see the [documentation](https://kusanagi.io/app#katana/docs), or join the [community](https://kusanagi.io/app#katana/community).

Support
-------

Please first read our [contribution guidelines](https://kusanagi.io/app#katana/open-source/contributing).

* [Requesting help](https://kusanagi.io/app#katana/open-source/help)
* [Reporting a bug](https://kusanagi.io/app#katana/open-source/bug)
* [Submitting a patch](https://kusanagi.io/app#katana/open-source/patch)
* [Security issues](https://kusanagi.io/app#katana/open-source/security)

We use [milestones](https://github.com/kusanagi/katana-sdk-python3/milestones) to track upcoming releases inline with our [versioning](https://kusanagi.io/app#katana/versioning) strategy, and as defined in our [roadmap](https://kusanagi.io/app#katana/roadmap).

For commercial support see the [solutions](https://kusanagi.io/solutions) available or [contact us](https://kusanagi.io/contact) for more information.

Contributing
------------

If you'd like to know how you can help and support our Open Source efforts see the many ways to [get involved](https://kusanagi.io/app#katana/open-source/get-involved).

Please also be sure to review our [community guidelines](https://kusanagi.io/app#katana/community/conduct).

License
-------

Copyright 2016-2017 KUSANAGI S.L. (https://kusanagi.io). All rights reserved.

KUSANAGI, the sword logo, KATANA and the "K" logo are trademarks and/or registered trademarks of KUSANAGI S.L. All other trademarks are property of their respective owners.

Licensed under the [MIT License](https://kusanagi.io/app#katana/open-source/license). Redistributions of the source code included in this repository must retain the copyright notice found in each file.
