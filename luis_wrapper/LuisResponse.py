
'''
Create an instance of the instance class if the values for the instance
exists in the value_dict.
parameters:
    instance_class: The class type the instance should be instantiated from.
    value_dict: dictionary containing the values used for instantiating the class.
    key: the key used to acces the class values.
    is_list: if true a list of objects will be created.
             if false a single object is created.
    '''
def _create_instance(instance_class, value_dict: dict, key: str, is_list=False):
    try:
        values = value_dict[key]
    except KeyError:
        return None
    else:
        if is_list:
            return [instance_class(x) for x in values]
        else:
            return instance_class(values)


class Response:
    def __init__(self, response: dict):
        self.json = response
        self.query = response['query']
        self.top_scoring_intent = Intent(response['topScoringIntent'])
        self.intents = [Intent(i) for i in response['intents']]
        self.entities = [Entity(e) for e in response['entities']]
        try:
            self.dialog = Dialog(response['dialog'])
        except KeyError:
            self.dialog = None
            self.need_more_info = False
        else:
            self.need_more_info = self.dialog.status != 'Finished'


class Intent:
    def __init__(self, intent: dict):
        self.name = intent['intent']
        self.score = intent['score']
        self.actions = [Action(a) for a in intent['actions']]
        # I am asuming that only one action can be triggered at a time
        for a in self.actions:
            if a.triggered:
                self.triggered_action = a
                break


class Entity:
    def __init__(self, entity: dict):
        self.type = entity['name']
        self.value = entity['entity']
        self.start_index = entity['startIndex']
        self.end_index = entity['endIndex']
        self.score = entity['score']
        self.resolution = entity['resolution'] # Not sure what this might return


class Action:
    def __init__(self, action: dict):
        self.name = action['name']
        self.triggered = action['triggered']
        self.parameters = [Parameter(p) for p in action['parameters']]


class Dialog:
    def __init__(self, dialog: dict):
        self.prompt = dialog['prompt']
        self.status = dialog['status'] #TODO: change to enum or something
        self.name = dialog['parameterName']
        self.parameter_type = dialog['parameterType']
        self.context_id = dialog['contextID']


class Parameter:
    def __init__(self, parameter: dict):
        self.name = parameter['name']
        self.type = parameter['type']
        self.required = parameter['required']
        self.value = Entity[parameter['value']]

    def __str__(self):
        return 'Parameter - {}'.format(self.name)

