import json
import requests

device_ids = ['21c099b3-d3e4-4d2e-a6e7-012aa611ef60']
package_version = '2.0.0'
package_name = 'hola'

data = json.dumps({
    'device_ids': device_ids,
    'package_version': package_version,
    'package_name': package_name,
})

server_address = '127.0.0.1:5000'
# server_address = '137.184.15.211:3636'

response = requests.post(f'http://{server_address}/rollout', data=data)
print(response)