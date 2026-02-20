from bot.commands import CommandArgs, CommandContext, CommandsRegistry
from bot.contacts import ContactAlreadyExistsError, ContactNotFoundError

bot_commands = CommandsRegistry()


@bot_commands.register("hello")
def say_hello() -> None:
    print("How can I help you?")


@bot_commands.register("add", args=["name"], optional_args=["phone number"])
def add_contact(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_contact(name, phone=phone):
            case "added":
                print("Contact added.")
            case "updated:phone":
                print("Phone number added.")
    except ContactAlreadyExistsError:
        print("Contact already exists.")


@bot_commands.register("change", args=["name", "old phone number", "new phone number"])
def change_phone(args: CommandArgs, context: CommandContext) -> None:
    name, old_phone, new_phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.update_contact(name, phone=(old_phone, new_phone))
        print("Contact updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register("phone", args=["name"])
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


@bot_commands.register("all")
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


@bot_commands.register("add-birthday", args=["name", "birthday"])
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


@bot_commands.register("show-birthday", args=["name"])
def show_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if contact:
        birthday = contact.get_birthday()
        print(birthday or "Contact doesn't have a birthday set.")
    else:
        print("Contact doesn't exist.")


@bot_commands.register("birthdays")
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


class StopCommandsLoop(Exception):
    pass


@bot_commands.register("exit", "close", "quit", "bye")
def say_goodbye() -> None:
    print("Good bye!")
    raise StopCommandsLoop
