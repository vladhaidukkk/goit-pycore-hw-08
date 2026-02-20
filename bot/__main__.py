import sys
from pathlib import Path

from bot.bot_commands import StopCommandsLoop, bot_commands
from bot.commands import (
    CommandNotFoundError,
    CommandsDispatcher,
    InvalidCommandArgumentsError,
)
from bot.contacts import ContactsBook, ContactsService

commands_dispatcher = CommandsDispatcher(bot_commands)


def parse_args(args: list[str]) -> Path:
    if len(args) > 1:
        print(f"Usage: python -m bot [path_to_contacts_book]")
        print(f"Expected 0 or 1 arguments, got {len(args)}")
        sys.exit(1)

    return Path(args[0]) if args else Path("contacts.pkl")


def load_contacts(path: Path) -> ContactsBook:
    try:
        return ContactsBook.from_file(path)
    except IsADirectoryError:
        print(f"File is expected, not a directory: '{path.name}'")
        sys.exit(1)


def handle_invalid_command_args_error(error: InvalidCommandArgumentsError) -> None:
    if error.required_args and error.optional_args:
        print(
            f"Give me {error.required_args_str} please, and optionally {error.optional_args_str}."
        )
    elif error.required_args:
        print(f"Give me {error.required_args_str} pleaserror.")
    elif error.optional_args:
        print(f"You can optionally provide {error.optional_args_str}.")
    else:
        print("This command doesn't take any arguments.")


def main() -> None:
    contacts_path = parse_args(sys.argv[1:])
    contacts = load_contacts(contacts_path)
    contacts_service = ContactsService(contacts)

    # Run commands in a loop
    print("Welcome to the assistant bot!")
    while True:
        command, command_args = commands_dispatcher.input_command("Enter a command: ")
        if not command:
            continue

        try:
            commands_dispatcher.run_command(
                command,
                *command_args,
                contacts=contacts,
                contacts_service=contacts_service,
            )
        except CommandNotFoundError:
            print("Invalid command.")
        except InvalidCommandArgumentsError as e:
            handle_invalid_command_args_error(e)
        except ValueError as e:
            print(e)
        except StopCommandsLoop:
            break
        except Exception as e:
            print(f"Whoops, an unexpected error occurred: {e}")

    # Save contacts at the end
    contacts.save(contacts_path)


if __name__ == "__main__":
    main()
