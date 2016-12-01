

class Response:
    need_more_info = False

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
    triggered_action = None

    def __init__(self, intent: dict):
        self.name = intent['intent']
        self.score = intent['score']
        try:
            self.actions = [Action(a) for a in intent['actions']]
        except KeyError:
            self.actions = None
            self.triggered_action = None
        else:
            self._find_triggered_action()

    def _find_triggered_action(self):
        self.triggered_action = None
        for a in self.actions:
            if a.triggered:
                self.triggered_action = a
                break


class Entity:
    def __init__(self, entity: dict):
        self.type = entity['type']
        self.value = entity['entity']
        self.start_index = entity['startIndex']
        self.end_index = entity['endIndex']
        self.score = entity['score']
        try:
            self.resolution = entity['resolution']  # Not sure what this might return
        except KeyError:
            self.resolution = None


class Action:
    def __init__(self, action: dict):
        self.name = action['name']
        self.triggered = action['triggered']
        self.parameters = [Parameter(p) for p in action['parameters']]


class Dialog:
    def __init__(self, dialog: dict):
        self.context_id = dialog['contextId']
        self.status = dialog['status'] #TODO: change to enum or something
        if self.status != 'Finished':
            self.prompt = dialog['prompt']
            self.name = dialog['parameterName']
            self.parameter_type = dialog['parameterType']


class Parameter:
    def __init__(self, parameter: dict):
        self.name = parameter['name']
        self.type = parameter['type']
        self.required = parameter['required']
        try:
            self.value = Entity(parameter['value'])
        except TypeError:
            self.value = None

    def __str__(self):
        return 'Parameter - {}'.format(self.name)

