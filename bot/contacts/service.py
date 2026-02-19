from typing import Literal

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook


class ContactsService:
    def __init__(self, contacts: ContactsBook) -> None:
        self._contacts = contacts

    def create_contact(self, name: str, *, phone: str | None = None) -> None:
        contact = self._contacts.find(name)
        if contact:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists.")

        contact = ContactRecord(name)
        if phone:
            contact.add_phone(phone)
        self._contacts.add_record(contact)

    def add_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
    ) -> Literal["added", "updated"]:
        contact = self._contacts.find(name)
        if not contact:
            self.create_contact(name, phone=phone)
            return "added"
        elif not contact.phones and phone:
            self.add_phone(name, phone=phone)
            return "updated"
        else:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists")

    def add_phone(self, name: str, *, phone: str) -> None:
        contact = self._contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_phone(phone)

    def add_birthday(
        self,
        name: str,
        *,
        birthday: str,
    ) -> Literal["added", "updated"]:
        contact = self._contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        had_birthday = contact.birthday is not None
        contact.add_birthday(birthday)
        return "updated" if had_birthday else "added"

    def get_contact(self, name: str) -> ContactRecord | None:
        return self._contacts.find(name)

    def update_contact(self, name: str, *, phone: tuple[str, str]) -> None:
        contact = self._contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.edit_phone(phone[0], phone[1])
