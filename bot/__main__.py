import sys
from pathlib import Path

from bot.commands import (
    CommandArgs,
    CommandContext,
    CommandNotFoundError,
    CommandsRegistry,
    InvalidCommandArgumentsError,
)
from bot.models import AddressBook, Record

commands = CommandsRegistry()


@commands.register("hello")
def say_hello() -> None:
    print("How can I help you?")


@commands.register("add", args=["name"], optional_args=["phone number"])
def add_contact(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    book = context["book"]

    record = book.find(name)
    if not record:
        record = Record(name)
        if phone:
            record.add_phone(phone)
        book.add_record(record)
        print("Contact added.")
    elif not record.phones and phone:
        record.add_phone(phone)
        print("Phone number added.")
    else:
        print("Contact already exists.")


@commands.register("change", args=["name", "old phone number", "new phone number"])
def change_contact(args: CommandArgs, context: CommandContext) -> None:
    name, old_phone, new_phone = args
    book = context["book"]

    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        print("Contact updated.")
    else:
        print("Contact doesn't exist.")


@commands.register("phone", args=["name"])
def show_phone(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    book = context["book"]

    record = book.find(name)
    if not record:
        print("Contact doesn't exist.")
        return

    if not record.phones:
        print("This contact doesn't have a phone number.")
        return

    print(record.phones[0])


@commands.register("all")
def show_all(context: CommandContext) -> None:
    book = context["book"]
    if book:
        print(
            "\n".join(
                f"{record.name}: {record.phones[0] if record.phones else '-'}"
                for record in book.values()
            )
        )
    else:
        print("No contacts.")


@commands.register("add-birthday", args=["name", "birthday"])
def add_birthday(args: CommandArgs, context: CommandContext) -> None:
    name, birthday = args
    book = context["book"]

    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        print("Birthday added.")
    else:
        print("Contact doesn't exist.")


@commands.register("show-birthday", args=["name"])
def show_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    book = context["book"]

    record = book.find(name)
    if record:
        birthday = record.get_birthday()
        print(birthday or "Contact doesn't have a birthday set.")
    else:
        print("Contact doesn't exist.")


@commands.register("birthdays")
def birthdays(context: CommandContext) -> None:
    book = context["book"]

    if not book:
        print("No contacts.")
        return

    if book.birthdays_count == 0:
        print("No contacts with birthdays.")
        return

    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        print("No contacts with upcoming birthdays.")
        return

    print(
        "\n".join(
            f"{upcoming_birthday['name']}: {upcoming_birthday['birthday']} (Congratulate: {upcoming_birthday['congratulation_date']})"
            for upcoming_birthday in upcoming_birthdays
        )
    )


class StopSession(Exception):
    pass


@commands.register("exit", "close", "quit", "bye")
def say_goodbye() -> None:
    raise StopSession


def parse_input(user_input: str) -> tuple[str, ...]:
    cmd, *args = user_input.split()
    cmd = cmd.lower()
    return cmd, *args


def main() -> None:
    # Parse CLI arguments to extract address book path
    args = sys.argv[1:]
    if len(args) > 1:
        print(f"Usage: python -m bot [path_to_address_book]")
        print(f"Expected 0 or 1 arguments, got {len(args)}")
        sys.exit(1)
    elif len(args) == 1:
        path = Path(args[0])
    else:
        path = None

    # Load address book from a file or create a new one
    if path:
        try:
            book = AddressBook.from_file(path)
        except IsADirectoryError:
            print(f"File is expected, not a directory: '{path.name}'")
            sys.exit(1)
    else:
        book = AddressBook()

    # Start bot session (commands loop)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *command_args = parse_input(user_input)
        try:
            commands.run(command, *command_args, book=book)
        except CommandNotFoundError:
            print("Invalid command.")
        except InvalidCommandArgumentsError as e:
            if e.required_args and e.optional_args:
                print(
                    f"Give me {e.required_args_str} please, and optionally {e.optional_args_str}."
                )
            elif e.required_args:
                print(f"Give me {e.required_args_str} please.")
            elif e.optional_args:
                print(f"You can optionally provide {e.optional_args_str}.")
            else:
                print("This command doesn't take any arguments.")
        except ValueError as e:
            print(e)
        except StopSession:
            print("Good bye!")
            break
        except Exception as e:
            print(f"Whoops, an unexpected error occurred: {e}")

    # Save address book at the end
    if path:
        book.save(path)


if __name__ == "__main__":
    main()
