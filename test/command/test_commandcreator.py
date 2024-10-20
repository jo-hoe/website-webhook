
from app.command.commandcreator import create_command
from app.command.getxpathvalue import GetXPathValue
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState


def test_create_trigger_callback_on_changed_state():
    data = {
        "kind": TriggerCallbackOnChangedState.KIND,
        "name": "b",
        "xpath": "c"
    }

    command = create_command(data, "d", False)

    assert isinstance(command, TriggerCallbackOnChangedState)
    assert command._kind == TriggerCallbackOnChangedState.KIND
    assert command._name == "b"
    assert command._xpath == "c"
    assert command._url == "d"

def test_create_get_xpath_value():
    data = {
        "kind": GetXPathValue.KIND,
        "name": "b",
        "xpath": "c"
    }

    command = create_command(data, "d", False)

    assert isinstance(command, GetXPathValue)
    assert command._kind == GetXPathValue.KIND
    assert command._name == "b"
    assert command._xpath == "c"
    assert command._url == "d"
