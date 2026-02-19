import sys
from pathlib import Path

from bot.commands import (
    CommandArgs,
    CommandContext,
    CommandNotFoundError,
    CommandsRegistry,
    InvalidCommandArgumentsError,
)
from bot.contacts import (
    ContactAlreadyExistsError,
    ContactNotFoundError,
    ContactsBook,
    ContactsService,
)

commands = CommandsRegistry()


@commands.register("hello")
def say_hello() -> None:
    print("How can I help you?")


@commands.register("add", args=["name"], optional_args=["phone number"])
def add_contact(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_contact(name, phone=phone):
            case "added":
                print("Contact added.")
            case "updated":
                print("Phone number added.")
    except ContactAlreadyExistsError:
        print("Contact already exists.")


@commands.register("change", args=["name", "old phone number", "new phone number"])
def change_phone(args: CommandArgs, context: CommandContext) -> None:
    name, old_phone, new_phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.update_contact(name, phone=(old_phone, new_phone))
        print("Contact updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@commands.register("phone", args=["name"])
def show_phone(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if not contact:
        print("Contact doesn't exist.")
        return

    if not contact.phones:
        print("This contact doesn't have a phone number.")
        return

    print(contact.phones[0])


@commands.register("all")
def show_all(context: CommandContext) -> None:
    contacts = context["contacts"]
    if contacts:
        print(
            "\n".join(
                f"{contact.name}: {contact.phones[0] if contact.phones else '-'}"
                for contact in contacts.values()
            )
        )
    else:
        print("No contacts.")


@commands.register("add-birthday", args=["name", "birthday"])
def add_birthday(args: CommandArgs, context: CommandContext) -> None:
    name, birthday = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_birthday(name, birthday=birthday):
            case "added":
                print("Birthday added.")
            case "updated":
                print("Birthday updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@commands.register("show-birthday", args=["name"])
def show_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if contact:
        birthday = contact.get_birthday()
        print(birthday or "Contact doesn't have a birthday set.")
    else:
        print("Contact doesn't exist.")


@commands.register("birthdays")
def birthdays(context: CommandContext) -> None:
    contacts = context["contacts"]

    if not contacts:
        print("No contacts.")
        return

    if contacts.birthdays_count == 0:
        print("No contacts with birthdays.")
        return

    upcoming_birthdays = contacts.get_upcoming_birthdays()
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
    # Parse CLI arguments to extract contacts book path
    args = sys.argv[1:]
    if len(args) > 1:
        print(f"Usage: python -m bot [path_to_contacts_book]")
        print(f"Expected 0 or 1 arguments, got {len(args)}")
        sys.exit(1)
    elif len(args) == 1:
        path = Path(args[0])
    else:
        path = None

    # Load contacts book from a file or create a new one
    if path:
        try:
            contacts = ContactsBook.from_file(path)
        except IsADirectoryError:
            print(f"File is expected, not a directory: '{path.name}'")
            sys.exit(1)
    else:
        contacts = ContactsBook()

    contacts_service = ContactsService(contacts)

    # Start bot session (commands loop)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *command_args = parse_input(user_input)
        try:
            commands.run(
                command,
                *command_args,
                contacts=contacts,
                contacts_service=contacts_service,
            )
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

    # Save contacts book at the end
    if path:
        contacts.save(path)


if __name__ == "__main__":
    main()
