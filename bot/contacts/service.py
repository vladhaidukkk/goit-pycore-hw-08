from typing import Literal

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook


class ContactsService:
    def __init__(self, contacts: ContactsBook) -> None:
        self._contacts = contacts

    def create_contact(self, name: str, *, phone: str | None = None) -> None:
        record = self._contacts.find(name)
        if record:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists.")

        record = ContactRecord(name)
        if phone:
            record.add_phone(phone)
        self._contacts.add_record(record)

    def add_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
    ) -> Literal["created", "updated"]:
        record = self._contacts.find(name)
        if not record:
            self.create_contact(name, phone=phone)
            return "created"
        elif not record.phones and phone:
            self.add_phone(name, phone=phone)
            return "updated"
        else:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists")

    def add_phone(self, name: str, *, phone: str) -> None:
        record = self._contacts.find(name)
        if not record:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        record.add_phone(phone)

    def get_contact(self, name: str) -> ContactRecord | None:
        return self._contacts.find(name)

    def update_contact(self, name: str, *, phone: tuple[str, str]) -> None:
        record = self._contacts.find(name)
        if not record:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        record.edit_phone(phone[0], phone[1])
