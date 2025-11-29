HTML_LINK_TAG = "a"
HTML_HREF = "href"
HTML_ID = "#"
HU_TOP_LEVEL_DOMAIN = "hu"
UK_TOP_LEVEL_DOMAIN = "uk"
GB_ISO_CODE = "GB"
NON_COUNTRY_TOP_LEVEL_DOMAIN_WITH_TWO_LETTERS: list[str] = ["eu, su"]
SLASH = "/"
SPACE = " "
BEAUTIFULSOUP_HTML_PARSER = "html.parser"
WEBPAGE_EXTENSIONS: set[str] = {"html", "htm", "php", "asp", "aspx", "jsp"}
EXTENSION_DOT = "."
EMAIL_REGEX = r"([a-zA-Z0-9_.+-]+@(?:[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,})"
SPACY_LANGUAGE_HUNGARIAN = "hu"
SPACY_LANGUAGE_ENGLISH = "en"
SPACY_ENTITY_PERSON_HUNGARIAN = "PER"
SPACY_ENTITY_PERSON_ENGLISH = "PERSON"
SPACY_MODEL_HU = "hu_core_news_lg"
SPACY_MODEL_EN = "en_core_web_lg"
NAME_REGEX = r"^([A-Z][a-záéíóöőúüű'’]*(?:-[A-Z][a-záéíóöőúüű'’]*)*(?: [A-Z][a-záéíóöőúüű'’]*(?:[A-Z][a-záéíóöőúüű'’]*)?(?:-[A-Z][a-záéíóöőúüű'’]*)*)+)$"
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
    "button",
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
    "time",
    "output",
    "summary",
}
PHONE_NUMBER_UNKNOWN_REGION = "ZZ"
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