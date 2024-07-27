

from app.command.command import Command


class MockCommand(Command):
    def execute(self) -> bool:
        return super().execute()

    def replace_placeholder(self, input: str) -> str:
        return super().replace_placeholder(input)


def test_replace_placeholder():
    command = MockCommand("a", "b", "c")
    assert command.replace_placeholder(
        "<<kind>><<name>><<url>>") == "abc", "replace_placeholder failed"
