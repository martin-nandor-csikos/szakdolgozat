WEBDRIVER_HEADLESS_ARGUMENT = "--headless"
WEBDRIVER_REMOTE_URL = "http://chrome_selenium:4444/wd/hub"
HU_TOP_LEVEL_DOMAIN = "hu"
UK_TOP_LEVEL_DOMAIN = "uk"
GB_ISO_CODE = "GB"
NON_COUNTRY_TOP_LEVEL_DOMAIN_WITH_TWO_LETTERS: list[str] = ["eu", "su"]
BEAUTIFULSOUP_HTML_PARSER = "html.parser"
WEBPAGE_EXTENSIONS: set[str] = {"html", "htm", "php", "asp", "aspx", "jsp"}
# EMAIL_REGEX regex was created by GitHub Copilot
EMAIL_REGEX = r"([a-zA-Z0-9_.+-]+@(?:[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,})"
SPACY_LANGUAGE_HUNGARIAN = "hu"
SPACY_LANGUAGE_ENGLISH = "en"
SPACY_ENTITY_PERSON_HUNGARIAN = "PER"
SPACY_ENTITY_PERSON_ENGLISH = "PERSON"
SPACY_MODEL_HU = "hu_core_news_lg"
SPACY_MODEL_EN = "en_core_web_lg"
# NAME_REGEX regex was created by GitHub Copilot
NAME_REGEX = r"^([A-Z][a-záéíóöőúüű'’]*(?:-[A-Z][a-záéíóöőúüű'’]*)*(?: [A-Z][a-záéíóöőúüű'’]*(?:[A-Z][a-záéíóöőúüű'’]*)?(?:-[A-Z][a-záéíóöőúüű'’]*)*)+)$"
# HTML_TEXT_TAGS was created by GitHub Copilot
HTML_TEXT_TAGS: set[str] = {
    "p",
    "a",
    "span",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "td",
    "th",
    "label",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "small",
    "mark",
    "blockquote",
    "cite",
    "code",
    "pre",
    "abbr",
    "q",
    "output",
    "summary",
}
PHONE_NUMBER_UNKNOWN_REGION = "ZZ"
# HEARTBEAT_MESSAGES was created by GitHub Copilot
HEARTBEAT_MESSAGES = [
    "Finding the best results for you...",
    "Sit tight and grab a cup of coffee...",
    "Operation in progress...",
    "Analyzing data...",
    "Don't worry, the program didn't freeze...yet...",
    "Loading... (insert elevator music here)",
    "Still parsing the website 4 real no cap",
    "Did you know? The password for the first computer was 'password'.",
    "Interesting fact: CAPTCHA stands for 'Completely Automated Public Turing test to tell Computers and Humans Apart'.",
    "Some interesting trivia: The first domain name ever registered was symbolics.com in 1985.",
]
ESSENTIAL_ADDRESS_COMPONENTS = ["city", "road", "postcode"]
LRU_CACHE_MAXSIZE = 2
MIN_ADDRESS_COMPONENTS = 3
MAX_ADDRESS_COMPONENTS = 10
HEARTBEAT_INTERVAL_SECONDS = 20