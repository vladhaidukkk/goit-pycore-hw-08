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
