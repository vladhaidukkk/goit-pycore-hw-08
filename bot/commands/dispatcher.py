import inspect
from typing import Any, get_type_hints

from .errors import ForbiddenCommandArgumentError, InvalidCommandArgumentsError
from .registry import CommandsRegistry

CommandArgs = tuple[str, ...]
CommandContext = dict[str, Any]


class CommandsDispatcher:
    def __init__(self, registry: CommandsRegistry) -> None:
        self._registry = registry

    def input_command(self, prompt: str) -> tuple[str | None, list[str]]:
        user_input = input(prompt).strip()
        if not user_input:
            return None, []

        command, *args = user_input.split()
        command = command.lower()
        return command, args

    def run_command(self, command_name: str, *args: str, **kwargs: Any) -> None:
        command = self._registry.get(command_name)
        command_args: dict[str, Any] = {}

        sig = inspect.signature(command.func)
        hints = get_type_hints(command.func)

        for param_name, _ in sig.parameters.items():
            param_type = hints.get(param_name)

            # Check args quantity & inject them
            if param_type == CommandArgs:
                required_args_n = len(command.required_args)
                optional_args_n = len(command.optional_args)
                min_args_n = required_args_n
                max_args_n = required_args_n + optional_args_n

                if max_args_n == 0 and len(args) > 0:
                    raise InvalidCommandArgumentsError(
                        f"Command '{command_name}' does not expect any args"
                    )
                elif not (min_args_n <= len(args) <= max_args_n):
                    raise InvalidCommandArgumentsError(
                        (
                            f"Command '{command_name}' requires {min_args_n} args"
                            if min_args_n == max_args_n
                            else f"Command '{command_name}' requires {min_args_n} (+{max_args_n} optional) args"
                        ),
                        required_args=command.required_args,
                        optional_args=command.optional_args,
                    )

                optional_defaults = (None,) * (max_args_n - len(args))
                command_args[param_name] = args + optional_defaults

            # Inject context
            if param_type == CommandContext:
                command_args[param_name] = kwargs

            # Forbid all other arguments
            if param_type != CommandArgs and param_type != CommandContext:
                raise ForbiddenCommandArgumentError(
                    f"Argument '{param_name}' with '{param_type}' type is not allowed."
                )

        command.func(**command_args)
