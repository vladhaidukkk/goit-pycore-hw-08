class ContactsError(Exception):
    pass


class ContactAlreadyExistsError(ContactsError):
    pass


class ContactNotFoundError(ContactsError):
    pass
