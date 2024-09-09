from flask import Flask, request, jsonify
import json
from jsonpath_ng import jsonpath, parse
import requests

app = Flask(__name__)

class SalesforceObjectInfo:
    def __init__(self, response):
        self.uiapi_record_json = response
        self.filtered_attributes = None
        self.filtered_attributes_data_type = None
        self.combined_attributes = None
        self.api_name_counts = {}

    def get_recent_items(self, url, version, object_name, token):
        try:
            # Construir la URL completa para la solicitud GET a Salesforce
            recent_items_url = f"{url}/services/data/{version}/sobjects/{object_name}"

            # Hacer la solicitud GET a Salesforce
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(recent_items_url, headers=headers)

            # Validar la respuesta de Salesforce
            if response.status_code != 200:
                raise RuntimeError(f'Error en la solicitud a Salesforce: {response.status_code}')

            # Analizar la respuesta JSON
            data = response.json()

            # Obtener los registros de recentItems y retornar el primer registro si hay al menos uno
            recent_items = data.get('recentItems', [])
            if recent_items:
                return recent_items[0]
            else:
                return None

        except Exception as e:
            raise RuntimeError(f'Error al obtener los registros recientes: {str(e)}')
    
    
    def api_name_getter(self):
        filtered_array = []

        try:
            label_path = parse('$.layouts..sections..layoutRows[*].layoutItems[*]')
            list_of_layout_items = [match.value for match in label_path.find(json.loads(self.uiapi_record_json))]

            for component in list_of_layout_items:
                if isinstance(component, dict):
                    if 'layoutComponents' in component:
                        sub_components = component['layoutComponents']
                        if isinstance(sub_components, list):
                            for sub_component in sub_components:
                                if isinstance(sub_component, dict):
                                    api_name = sub_component.get('apiName', '')
                                    label = sub_component.get('label', '')

                                    if len(sub_components) == 1:
                                        label = component.get('label', '')
                                        if not label:
                                            label = sub_component.get('label', '')

                                    if api_name and label:
                                        filtered_object = {'apiName': api_name, 'label': label}
                                        filtered_array.append(filtered_object)

            self.filtered_attributes = filtered_array
            #print("Filtered apiNameGetter:", filtered_array)

        except Exception as e:
            raise RuntimeError("Error list apiNames." + str(e))

    def data_type_getter(self):
        filtered_array = []

        try:
            label_path = parse('$..objectInfos..fields')
            list_of_labels = [match.value for match in label_path.find(json.loads(self.uiapi_record_json))]

            for row in list_of_labels:
                if isinstance(row, dict):
                    for field_name, field_info in row.items():
                        if 'updateable' in field_info and field_info['updateable']:
                            api_name = field_info.get('apiName', '')
                            filtered_object = {'apiName': api_name, 'dataType': field_info.get('dataType', '')}
                            filtered_array.append(filtered_object)

            self.filtered_attributes_data_type = filtered_array
            #print("Filtered dataTypeGetter:", filtered_array)

        except Exception as e:
            raise RuntimeError("Error list apiNames." + str(e))

    def combined_attributes_getter(self):
        self.api_name_getter()
        self.data_type_getter()

        combined_array = []

        for api_name_obj in self.filtered_attributes:
            api_name = api_name_obj['apiName']

            for data_type_obj in self.filtered_attributes_data_type:
                data_type_api_name = data_type_obj['apiName']

                if api_name == data_type_api_name:
                    combined_object = {
                        'apiName': api_name,
                        'label': api_name_obj['label'],
                        'dataType': data_type_obj['dataType']
                    }
                    combined_array.append(combined_object)
                    break

        self.combined_attributes = combined_array
        print("Combined Attributes:", combined_array)
        return combined_array

@app.route('/', methods=['POST'])
def salesforce_data():
    try:
        # Recuperar parámetros de la solicitud POST
        url = request.form.get('url')
        version = request.form.get('version')
        object_name = request.form.get('object_name')
        token = request.form.get('token')

        # Validar que todos los parámetros necesarios estén presentes
        if not all([url, version, object_name, token]):
            return jsonify({'error': 'Se requieren todos los parámetros: url, version, object_name, token'})

        # Crear una instancia de SalesforceObjectInfo
        salesforce_info = SalesforceObjectInfo(None)

        # Obtener el registro reciente para obtener el record_id
        recent_item = salesforce_info.get_recent_items(url, version, object_name, token)

        # Obtener el record_id del registro reciente
        if recent_item:
            record_id = recent_item.get('Id')
        else:
            return jsonify({'error': 'No se encontró un registro reciente.'})

        # Construir la URL completa para la solicitud GET a Salesforce
        salesforce_url = f"{url}/services/data/{version}/ui-api/record-ui/{record_id}?formFactor=Large&modes=View,Edit"

        # Hacer la solicitud GET a Salesforce
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(salesforce_url, headers=headers)

        # Validar la respuesta de Salesforce
        if response.status_code != 200:
            return jsonify({'error': f'Error en la solicitud a Salesforce: {response.status_code}'})

        # Crear una instancia de SalesforceObjectInfo con la respuesta
        salesforce_info = SalesforceObjectInfo(response.text)

        # Obtener los combined_attributes y devolverlos como respuesta JSON
        combined_attributes = salesforce_info.combined_attributes_getter()
        return jsonify(combined_attributes)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)