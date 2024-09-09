# Salesforce API Frmk

Este repositorio contiene clases para interactuar con Salesforce y obtener información sobre objetos y atributos utilizando el servicio UI API.

### Obtener token
- EndPoint -> https://zorem-dev-ed.develop.my.salesforce.com/services/oauth2/token?
- Parametros GET
- **grant_type:**
- **client_id:**
- **client_secret:**
- **username:**
- **password:**

### Respuesta
- **response:** Del response obtenido es necesario recuperar el access_token.

### Obtener Atributos de un formulario
- EndPoint -> http://salesforce.zorem.pe/
- Parametros POST FORM
- **url:** La url del proyecto salesforce.
- **version:** Versión de la API (ejemplo: v54.0).
- **object_name:** Identificador del registro en Salesforce, se obtiene de la url al ingresar al detalle de un registro (ejemplo: Account/001Hr00001vZf3qIAC/view).
- **token:** Token de autorización de Salesforce.

### Respuesta
- **response:** El response obtenido sera un Json con los atributos del formulario requerido.
```
[
     {
        "apiName": "Name",
        "dataType": "String",
        "label": "Account Name"
    },
    {
        "apiName": "Phone",
        "dataType": "Phone",
        "label": "Phone"
    },
    {
        "apiName": "Website",
        "dataType": "Url",
        "label": "Website"
    },
    {
        "apiName": "ShippingCity",
        "dataType": "String",
        "label": "Shipping City"
    },
    {
        "apiName": "AnnualRevenue",
        "dataType": "Currency",
        "label": "Annual Revenue"
    },
    {
        "apiName": "ShippingState",
        "dataType": "String",
        "label": "Shipping State/Province"
    }
]
```
### Como usarlo...
```
SalesforceObjectInfo salesforceObjectInfo = new SalesforceObjectInfo("Account");

            salesforceObjectInfo.formValueFiller("Name",name);
            salesforceObjectInfo.formValueFiller("Phone",phone);
            salesforceObjectInfo.formValueFiller("Website",website);
            salesforceObjectInfo.formValueFiller("ShippingCity",employees);
            salesforceObjectInfo.formValueFiller("AnnualRevenue",annual_revenue);
            salesforceObjectInfo.formValueFiller("ShippingState",description);
