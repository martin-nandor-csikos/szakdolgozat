from enum import Enum

class ExportChoice(Enum):
    EXPORT = 'y'
    NO_EXPORT = 'n'

class CsvHeaderText(Enum):
    NAMES = 'Names (found at link)'
    EMAILS = 'Emails (found at link)'
    PHONE_NUMBERS = 'Phone numbers (found at link)'
    ADDRESSES = 'Addresses (found at link)'