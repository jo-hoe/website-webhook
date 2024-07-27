
from app.command.commandcreator import create_command
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState


def test_create_trigger_callback_on_changed_state():
    data = {
        "kind": TriggerCallbackOnChangedState.KIND,
        "name": "b",
        "xpath": "c"
    }

    command = create_command(data, "d")

    assert isinstance(command, TriggerCallbackOnChangedState)
    assert command._kind == TriggerCallbackOnChangedState.KIND
    assert command._name == "b"
    assert command._xpath == "c"
    assert command._url == "d"
