import inspect
from typing import Any, Callable, NamedTuple, get_type_hints


class CommandError(Exception):
    pass


class CommandAlreadyExistsError(CommandError):
    pass


class CommandNotFoundError(CommandError):
    pass


class ForbiddenCommandArgumentError(CommandError):
    pass


class InvalidCommandArgumentsError(CommandError):
    def __init__(
        self,
        message: str,
        *,
        required_args: list[str] | None = None,
        optional_args: list[str] | None = None,
    ) -> None:
        self.required_args = required_args or []
        self.optional_args = optional_args or []
        super().__init__(message)

    @property
    def required_args_str(self) -> str:
        return self._format_args(self.required_args)

    @property
    def optional_args_str(self) -> str:
        return self._format_args(self.optional_args)

    @staticmethod
    def _format_args(args: list[str]) -> str:
        if len(args) > 1:
            return ", ".join(args[:-1]) + " and " + args[-1]
        elif len(args) == 1:
            return args[0]
        else:
            return ""


CommandArgs = tuple[str, ...]
CommandContext = dict[str, Any]


class Command(NamedTuple):
    name: str
    func: Callable
    required_args: list[str]
    optional_args: list[str]


class CommandsRegistry:
    def __init__(self) -> None:
        self._commands_registry: dict[str, Command] = {}

    def register(
        self,
        *command_names: str,
        args: list[str] | None = None,
        optional_args: list[str] | None = None,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            for name in command_names:
                if name in self._commands_registry:
                    raise CommandAlreadyExistsError(
                        f"Command '{name}' is already registered."
                    )
                self._commands_registry[name] = Command(
                    name=name,
                    func=func,
                    required_args=args or [],
                    optional_args=optional_args or [],
                )
            return func

        return decorator

    def get(self, command_name: str) -> Command:
        command = self._commands_registry.get(command_name)
        if not command:
            raise CommandNotFoundError(f"Command '{command_name}' is not registered.")
        return command

    def run(self, command_name: str, *args: str, **kwargs: Any) -> None:
        command = self.get(command_name)
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
