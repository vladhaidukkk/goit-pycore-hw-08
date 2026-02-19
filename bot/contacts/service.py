from typing import Literal

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook


class ContactsService:
    def __init__(self, contacts: ContactsBook) -> None:
        self._contacts = contacts

    def create_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
        birthday: str | None = None,
    ) -> None:
        contact = self._contacts.find(name)
        if contact:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists.")

        contact = ContactRecord(name)
        if phone:
            contact.add_phone(phone)
        if birthday:
            contact.add_birthday(birthday)
        self._contacts.add_record(contact)

    def add_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
        birthday: str | None = None,
    ) -> str:
        contact = self._contacts.find(name)
        if not contact:
            self.create_contact(name, phone=phone)
            return "added"

        updated = []
        if not contact.phones and phone:
            self.add_phone(name, phone=phone)
            updated.append("phone")
        if not contact.birthday and birthday:
            self.add_birthday(name, birthday=birthday)
            updated.append("birthday")

        if updated:
            return f"updated:{'|'.join(updated)}"

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

    def update_contact(
        self,
        name: str,
        *,
        phone: tuple[str, str] | None,
        birthday: str | None = None,
    ) -> None:
        contact = self._contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        if phone:
            contact.edit_phone(phone[0], phone[1])
        if birthday:
            contact.add_birthday(birthday)
