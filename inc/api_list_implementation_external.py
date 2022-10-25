import os
import logging
import requests
import json
import jsonpickle
import apie
import eons
from api_operation_implementation_external import operation_implementation_external

class list_implementation_external(operation_implementation_external):
    def __init__(this, name="external list implementation", implements="list"):
        super().__init__(name, implements)

        this.optionalKWArgs['fields_arg_name'] = "_fields[]"

    # Required Endpoint method. See that class for details.
    def GetHelpText(this):
        return f'''\
List anything by offloading the retrieval work to another API.
This does not have direct access to the local filesystem or databases.

Per the parent 'external':
{super().GetHelpText()}
'''

    def MapData(this):
        this.query_map['page'] = 'implemented.page'
        this.query_map['per_page'] = 'implemented.per_page'

        super().MapData()

        # Setting query_map vars before super().MapData guarantees that the query will have a '?'.

        # The Fields arg is repeated, which is not as easy / intuitive to do with a python dictionary.
        if (this.implemented.fields):
            fieldParam = f"&{this.fields_arg_name}="
            for field in this.implemented.fields:
                this.url += fieldParam + fieldParam.join(this.fields)

    def PrepareResponse(this):
        super().PrepareResponse()
        if (this.implemented.make_list_of):
            responseJson = json.loads(this.response.content.string)
            responseList = []
            for node in responseJson:
                responseList.append(node[this.implemented.make_list_of])
            this.response.content.string = jsonpickle.encode(responseList)

    # This will be called from the list operation. Thus, this.precursor = *this and this = the list operation itself.
    @eons.method(propagate=True)
    def list_implementation(this):
        this.clobberContent = False
        this.precursor.MakeExternalCall()
        this.response = this.precursor.response