

from app.command.command import Command


class MockCommand(Command):
    def execute(self) -> bool:
        return super().execute()

    def replace_placeholder(self, input: str) -> str:
        return super().replace_placeholder(input)


def test_replace_placeholder():
    command = MockCommand("mock", "test-name", "test-url")
    assert command.replace_placeholder(
        "<<kind>> <<commands.test-name.name>> <<url>>") == "mock test-name test-url", "replace_placeholder failed"
