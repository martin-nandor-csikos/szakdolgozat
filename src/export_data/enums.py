from enum import Enum

class ExportChoice(Enum):
    EXPORT = 'y'
    NO_EXPORT = 'n'

class WebparserCsvHeaderText(Enum):
    NAMES = 'Names (found at link)'
    EMAILS = 'Emails (found at link)'
    PHONE_NUMBERS = 'Phone numbers (found at link)'
    ADDRESSES = 'Addresses (found at link)'

class ProfilesCsvHeaderText(Enum):
    NAME = 'Name'
    LINKEDIN_PROFILE = 'LinkedIn Profile URL'