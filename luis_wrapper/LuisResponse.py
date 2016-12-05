

class Response:
    """A class representing a LUIS response

    Attributes
    ----------
    json: json
        The original json response.
    query: str
        The query sent by the user
    top_scoring_intent_ Intent
        The most likely intent given the query
    intents : list[Intent]
        A list of all intents in the LUIS model.
        Each intent contains the score for how likely ot is the best fit for the current query
    entities: list[Entity]
        List of entities observed in the query
    need_more_info: bool
        Flag indicating whether more information has been requested by LUIS to trigger an action
    dialog: Dialog
        Dialog attached to the response.
        Will be None unless more information is requested or this is part of an ongoing conversation
    """
    def __init__(self, response: dict):
        """

        Parameters
        ----------
        response : dict
            Dictionary containing the values needed for initializing the Parameter.
            The values has to be immediately accessible from the dictionary.
        """
        self.json = response
        self.query = response['query']
        self.top_scoring_intent = Intent(response['topScoringIntent'])
        # Creating the entities has to be done before creating intents.
        # The Actions in created in an intent needs to be able to perform
        # A lookup in the entity list
        self.entities = [Entity(e) for e in response['entities']]
        self.intents = [Intent(i) for i in response['intents']]

        try:
            self.dialog = Dialog(response['dialog'])
        except KeyError:
            self.dialog = None
            self.need_more_info = False
        else:
            self.need_more_info = self.dialog.status != 'Finished'


class Intent:
    """A class representing a LUIS intent

    Attributes
    ----------
    name : str
        Name of the intent
    score : double
        The score (probability??) of intent of the query being this intent
    actions: list[Action]
        List of actions associated with this intent.
        Currently (Dec 2016) it is only ossible to have one action per intent
    triggered_action: Action
        The action that has been triggered by this intent
        Will be none if no actions have been triggered or no actions exists for this intent

    """

    def __init__(self, intent: dict):
        """

        Parameters
        ----------
        intent : dict
            Dictionary containing the values needed for initializing the Parameter.
            The values has to be immediately accessible from the dictionary.
        """
        self.name = intent['intent']
        self.score = intent['score']
        try:
            self.actions = [Action(a) for a in intent['actions']]
        except KeyError:
            self.actions = None
            self.triggered_action = None
        else:
            self.triggered_action = self._find_triggered_action()

    def _find_triggered_action(self):
        # Currently there can only be one action per Intent, but it might change in the future
        assert len(self.actions) == 1
        return self.actions[0]


class BaseEntity:
    """A class representing a basic LUIS entity without information about placement and score.

    Attributes
    ----------
    type : str
        The entity type
    value : str
        The value of the entity
    resolution: str
        Not sure what this is
        # TODO: Figure out what kind of object the resolution is
    """
    def __init__(self, entity: dict):
        """

        Parameters
        ----------
        entity : dict
            Dictionary containing the values needed for initializing the BaseEntity.
            The values has to be immediately accessible from the dictionary.
        """
        self.type = entity['type']
        self.value = entity['entity']
        try:
            self.resolution = entity['resolution']
        except KeyError:
            self.resolution = None


class Entity(BaseEntity):
    """A class representing a LUIS entity

    Attributes
    ----------
    type : str
        The entity type
    value : str
        The value of the entity
    start_index : int
        The index of the first letter of the entity in the query string
    end_index: int
        The index of the last letter of the entity in the query string
    score : double
        The score (probability??) of this entity being correct
    resolution: str
        Not sure what this is
        # TODO: Figure out what kind of object the resolution is
    """
    def __init__(self, entity: dict):
        """

        Parameters
        ----------
        entity : dict
            Dictionary containing the values needed for initializing the Entity.
            The values has to be immediately accessible from the dictionary.
        """
        super(Entity, self).__init__(entity)
        self.start_index = entity['startIndex']
        self.end_index = entity['endIndex']
        self.score = entity['score']



class Action:
    """A class representing a LUIS action

    Attributes
    ----------
    name : str
        The name of the action
    triggered : bool
        Flag indicating whether the action has been triggered
    parameters : List[Parameter]
        The list of parameters associated with this action
    """
    def __init__(self, action: dict):
        """

        Parameters
        ----------
        action : dict
            Dictionary containing the values needed for initializing the Parameter.
            The values has to be immediately accessible from the dictionary.
        """
        self.name = action['name']
        self.triggered = action['triggered']
        self.parameters = [Parameter(p) for p in action['parameters']]


class Dialog:
    """A class representing a LUIS dialog

    Attributes
    ----------
    context_id : str (as a GUID)
        The id of the dialog
    status : str
        The status of the dialog.
        Currently known possible statuses:
            * Question - More information is needed before the action associated with the recognized intent can be triggered
            * Finished - All needed information has been collected.

    The following attributes are only set if the status is not Finished
    prompt : str
        Prompt returned by LUIS to fill out missing info to trigger the associated action
    name : str
        Name given by the LUIS model designer to the parameter that triggered this dialog
    parameter_type : str
        Type of the Entity that is associated with this dialog.
    """
    def __init__(self, dialog: dict):
        """

        Parameters
        ----------
        dialog : dict
            Dictionary containing the values needed for initializing the Parameter.
            The values has to be immediately accessible from the dictionary.
        """
        self.context_id = dialog['contextId']
        self.status = dialog['status']  # TODO: change to enum or something
        if self.status != 'Finished':
            self.prompt = dialog['prompt']
            self.name = dialog['parameterName']
            self.parameter_type = dialog['parameterType']
        else:
            self.prompt = None
            self.name = None
            self.parameter_type = None


class Parameter:
    """A class representing a LUIS parameter

        Attributes
        ----------
        name : str
            Parameter name
        type: str
            Entity type used in the parameter
        required: bool
            Flag indicating whether the entity described by this parameter is needed to trigger the
            action it is associated with
        value: list[Entity]
            The entities associated with the parameter.
            Will be None if no entities of the correct type are present in the text
        """
    def __init__(self, parameter: dict):
        """

        Parameters
        ----------
        parameter : dict
            Dictionary containing the values needed for initializing the Parameter.
            The values has to be immediately accessible from the dictionary.
        """
        self.name = parameter['name']
        self.type = parameter['type']
        self.required = parameter['required']
        try:
            self.value = [BaseEntity(e) for e in parameter['value']]
        except KeyError:
            self.value = None
        except TypeError:
            self.value = None

    def __str__(self):
        return 'Parameter - {}'.format(self.name)
