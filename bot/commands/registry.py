import inspect
from typing import Any, Callable, NamedTuple, get_type_hints

from .errors import (
    CommandAlreadyExistsError,
    CommandNotFoundError,
    ForbiddenCommandArgumentError,
    InvalidCommandArgumentsError,
)

CommandArgs = tuple[str, ...]
CommandContext = dict[str, Any]


class Command(NamedTuple):
    name: str
    func: Callable
    required_args: list[str]
    optional_args: list[str]


class CommandsRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, Command] = {}

    def register(
        self,
        *command_names: str,
        args: list[str] | None = None,
        optional_args: list[str] | None = None,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            for name in command_names:
                if name in self._registry:
                    raise CommandAlreadyExistsError(
                        f"Command '{name}' is already registered."
                    )
                self._registry[name] = Command(
                    name=name,
                    func=func,
                    required_args=args or [],
                    optional_args=optional_args or [],
                )
            return func

        return decorator

    def get(self, command_name: str) -> Command:
        command = self._registry.get(command_name)
        if not command:
            raise CommandNotFoundError(f"Command '{command_name}' is not registered.")
        return command
