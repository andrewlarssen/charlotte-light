import json
import os
import boto3
from alexa.skills.smarthome import AlexaResponse
from datetime import datetime

# namespaces
NAMESPACE_CONTROL = "Alexa.PowerController"
NAMESPACE_DISCOVERY = "Alexa.Discovery"
NAMESPACE_AUTH = "Alexa.Authorization"
NAMESPACE_BRIGHTNESS = "Alexa.BrightnessController"
NAMESPACE_COLOR = "Alexa.ColorController"
NAMESPACE_SCENE = "Alexa.SceneController"
NAMESPACE_MODE = "Alexa.ModeController"

# discovery
REQUEST_DISCOVER = "Discover"
RESPONSE_DISCOVER = "Discover.Response"

#
REQUEST_GRANT = "AcceptGrant"
RESPONSE_GRANT = "AcceptGrant.Response"

# control
REQUEST_TURN_ON = "TurnOn"
REQUEST_TURN_OFF = "TurnOff"

mqtt_client = boto3.client('iot-data', region_name='eu-west-1')
dynamo_client = boto3.client('dynamodb', region_name='eu-west-1')


def lambda_handler(event, context):
    print(f"---- Request ----\n{json.dumps(event)}")

    if context is not None:
        print(f"---- Context ----\n{context}")

    print(f"---- Env ----\n{os.environ}")

    if 'directive' not in event:
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INVALID_DIRECTIVE',
                     'message': 'Missing key: directive, Is the request a valid Alexa Directive?'})
        return send_response(aer.get())

    directive = event['directive']
    header = directive['header']

    payload_version = header['payloadVersion']
    if payload_version != '3':
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INTERNAL_ERROR',
                     'message': 'This skill only supports Smart Home API version 3'})
        return send_response(aer.get())

    name = header['name']
    namespace = header['namespace']

    if (namespace == NAMESPACE_DISCOVERY and name == REQUEST_DISCOVER):
        return send_response(handle_discovery(event))
    elif (namespace == NAMESPACE_CONTROL):
        return send_response(handle_control(name, event))
    elif (namespace == NAMESPACE_BRIGHTNESS):
        return send_response(handle_brightness(name, event))
    elif (namespace == NAMESPACE_MODE):
        return send_response(handle_mode(name, event))
    elif (namespace == NAMESPACE_COLOR):
        return send_response(handle_color(name, event))
    elif (namespace == NAMESPACE_AUTH and name == REQUEST_GRANT):
        return send_response(handle_auth(namespace))
    else:
        return send_response(handle_unexpected_info(namespace))


def send_response(response):
    print(f"---- Response ----\n{json.dumps(response)}")
    return response


def handle_auth(event):
    grant_code = event['directive']['payload']['grant']['code']
    grantee_token = event['directive']['payload']['grantee']['token']
    aar = AlexaResponse(namespace=NAMESPACE_AUTH, name=RESPONSE_GRANT)
    return aar.get()


def handle_discovery(event):
    adr = AlexaResponse(namespace=NAMESPACE_DISCOVERY, name=RESPONSE_DISCOVER)
    capability_alexa = adr.create_payload_endpoint_capability()
    capability_alexa_powercontroller = adr.create_payload_endpoint_capability(
        interface=NAMESPACE_CONTROL,
        supported=[{'name': 'powerState'}])

    capability_alexa_brightnesscontroller = adr.create_payload_endpoint_capability(
        interface=NAMESPACE_BRIGHTNESS,
        supported=[{'name': 'brightness'}])

    capability_alexa_colorcontroller = adr.create_payload_endpoint_capability(
        interface=NAMESPACE_COLOR,
        supported=[{'name': 'color'}])

    capability_alexa_modecontroller = adr.create_payload_endpoint_capability(
        interface=NAMESPACE_MODE,
        supported=[{'name': 'mode'}])

    capability_alexa_modecontroller['instance'] = 'CharlotteLight.LightMode'
    capability_alexa_modecontroller['capabilityResources'] = {
        "friendlyNames": [
            {
                "@type": "text",
                "value": {
                    "text": "mode",
                    "locale": "en-GB"
                }
            },
            {
                "@type": "text",
                "value": {
                    "text": "light mode",
                    "locale": "en-GB"
                }
            },
            {
                "@type": "text",
                "value": {
                    "text": "pattern",
                    "locale": "en-GB"
                }
            },
            {
                "@type": "text",
                "value": {
                    "text": "color mode",
                    "locale": "en-GB"
                }
            }
        ]
    }

    capability_alexa_modecontroller['configuration'] = {
        "ordered": False,
        "supportedModes": [
            {
                "value": "LightMode.SingleColor",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "normal",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "single color",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            },
            {
                "value": "LightMode.Knightrider",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "knightrider",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "night rider",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "scroll",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "cylon",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            },
            {
                "value": "LightMode.Starburst",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "stars",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "starburst",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            },
            {
                "value": "LightMode.SlowRainbow",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "rainbow",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "slow rainbow",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            },
            {
                "value": "LightMode.FastRainbow",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "fast rainbow",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "chase rainbow",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "cinema chase rainbow",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            },
            {
                "value": "LightMode.Emergency",
                "modeResources": {
                    "friendlyNames": [
                        {
                            "@type": "text",
                            "value": {
                                "text": "emergency",
                                "locale": "en-GB"
                            }
                        },
                        {
                            "@type": "text",
                            "value": {
                                "text": "emergency lights",
                                "locale": "en-GB"
                            }
                        }
                    ]
                }
            }
        ]
    }

    capability_alexa_scenecontroller = adr.create_payload_endpoint_capability(
        interface=NAMESPACE_SCENE)

    adr.add_payload_endpoint(
        friendly_name='Charlotte Light',
        endpoint_id='charlotte-light-01',
        manufacturer_name='Larssen Inc',
        description='NeoPixel Light',
        display_categories= ["LIGHT"],
        capabilities=[
          capability_alexa,
          capability_alexa_powercontroller,
          capability_alexa_brightnesscontroller,
          capability_alexa_colorcontroller,
          capability_alexa_modecontroller,
          capability_alexa_scenecontroller])
    return adr.get()



def handle_control(name, event):
    endpoint_id = event['directive']['endpoint']['endpointId']
    power_state_value = 'OFF' if name == 'TurnOff' else 'ON'
    correlation_token = event['directive']['header']['correlationToken']

    state_sent = send_device_state(endpoint_id=endpoint_id, state='powerState', value=power_state_value)
    if not state_sent:
        return AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}).get()

    state_save = save_device_state(endpoint_id=endpoint_id, state='powerState', value=power_state_value)
    if not state_save:
        return AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach dynamo.'}).get()

    apcr = AlexaResponse(correlation_token=correlation_token)
    apcr.add_context_property(namespace=NAMESPACE_CONTROL, name='powerState', value=power_state_value, endpoint_id=endpoint_id)
    return apcr.get()


def handle_brightness(name, event):
    endpoint_id = event['directive']['endpoint']['endpointId']
    correlation_token = event['directive']['header']['correlationToken']

    if name == "SetBrightness":
        brightness = event['directive']['payload']['brightness']
    elif name == "AdjustBrightness":
        brightness_delta = event['directive']['payload']['brightnessDelta']
        brightness = 50
    elif name == "StateReport":
        brightness = False

    if brightness:
        neo_brightness = round(brightness * 255 / 100)
        state_sent = send_device_state(endpoint_id=endpoint_id, state='SetBrightness', value=neo_brightness)
        if not state_sent:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}).get()

        state_save = save_device_state(endpoint_id=endpoint_id, state='SetBrightness', value=brightness)
        if not state_save:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach dynamo.'}).get()

    apcr = AlexaResponse(correlation_token=correlation_token)
    apcr.add_context_property(namespace=NAMESPACE_BRIGHTNESS, name='brightness', value=brightness, endpoint_id=endpoint_id)
    return apcr.get()


def handle_color(name, event):
    endpoint_id = event['directive']['endpoint']['endpointId']
    correlation_token = event['directive']['header']['correlationToken']

    if name == "SetColor":
        color = event['directive']['payload']['color']
        neo_color = dict()
        neo_color["hue"] = round(color["hue"] * 65536 / 360)
        neo_color["saturation"] = round(color["saturation"] * 255)
        neo_color["brightness"] = round(color["brightness"] * 255)

    elif name == "StateReport":
        color = False

    if color:
        state_sent = send_device_state(endpoint_id=endpoint_id, state='SetColor', value=neo_color)
        if not state_sent:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}).get()

        state_save = save_device_state(endpoint_id=endpoint_id, state='SetColor', value=color)
        if not state_save:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach dynamo.'}).get()

    apcr = AlexaResponse(correlation_token=correlation_token)
    apcr.add_context_property(namespace=NAMESPACE_COLOR, name='color', value=color, endpoint_id=endpoint_id)
    return apcr.get()


def handle_mode(name, event):
    endpoint_id = event['directive']['endpoint']['endpointId']
    correlation_token = event['directive']['header']['correlationToken']

    if name == "SetMode":
        mode = event['directive']['payload']['mode']
        if mode == 'LightMode.SingleColor':
            neo_mode = 1
        elif mode == 'LightMode.Knightrider':
            neo_mode = 2
        elif mode == 'LightMode.Starburst':
            neo_mode = 3
        elif mode == 'LightMode.SlowRainbow':
            neo_mode = 4
        elif mode == 'LightMode.FastRainbow':
            neo_mode = 5
        elif mode == 'LightMode.Emergency':
            neo_mode = 6

    elif name == "StateReport":
        mode = False

    if mode:
        state_sent = send_device_state(endpoint_id=endpoint_id, state='SetMode', value=neo_mode)
        if not state_sent:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}).get()

        state_save = save_device_state(endpoint_id=endpoint_id, state='SetMode', value=mode)
        if not state_save:
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach dynamo.'}).get()

    apcr = AlexaResponse(correlation_token=correlation_token)
    apcr.add_context_property(namespace=NAMESPACE_MODE, name='mode', value=mode, endpoint_id=endpoint_id)
    return apcr.get()

def handle_unexpected_info(namespace):
    return AlexaResponse(
        name='ErrorResponse',
        payload={'type': 'INVALID_DIRECTIVE', 'message': f'Unknown namespace: {namespace}'}).get()


def save_device_state(endpoint_id, state, value):
    current_time = datetime.now()

    if state == 'SetBrightness':
        dynamo_response = dynamo_client.update_item(
        TableName='CharlotteLight',
        Key={'ItemId': {'S': endpoint_id}},
        UpdateExpression=f"SET {state} = :value, updated_at = :time, updated_int = :timestamp",
        ExpressionAttributeValues={
            ":value": {"N": str(value)},
            ":time": {"S": current_time.isoformat()},
            ":timestamp": {"N": str(current_time.timestamp())}})
    elif state == 'SetColor':
        dynamo_response = dynamo_client.update_item(
        TableName='CharlotteLight',
        Key={'ItemId': {'S': endpoint_id}},
        UpdateExpression=f"SET SetColor = :color, updated_at = :time, updated_int = :timestamp",
        ExpressionAttributeValues={
            ":color": {"M": {
                "hue": {"N": str(value['hue'])},
                "saturation": {"N": str(value['saturation'])},
                "brightness": {"N": str(value['brightness'])}
            }},
            ":time": {"S": current_time.isoformat()},
            ":timestamp": {"N": str(current_time.timestamp())}})
    else:
        dynamo_response = dynamo_client.update_item(
        TableName='CharlotteLight',
        Key={'ItemId': {'S': endpoint_id}},
        UpdateExpression=f"SET {state} = :value, updated_at = :time, updated_int = :timestamp",
        ExpressionAttributeValues={
            ":value": {"S": str(value)},
            ":time": {"S": current_time.isoformat()},
            ":timestamp": {"N": str(current_time.timestamp())}})

    print(f"---- Dynamo response ----\n{dynamo_response}")

    return( dynamo_response['ResponseMetadata']['HTTPStatusCode'] == 200)


def send_device_state(endpoint_id, state, value):
    mqtt_response = mqtt_client.publish(
        topic=f'device/{endpoint_id}/control',
        qos=1,
        payload=json.dumps({state: value})
    )

    print(f"---- MQTT response ----\n{mqtt_response}")

    return (mqtt_response['ResponseMetadata']['HTTPStatusCode'] == 200)
