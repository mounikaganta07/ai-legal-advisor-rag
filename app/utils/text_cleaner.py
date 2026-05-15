import re

def clean_legal_text(text):

    text = re.sub(
        r'\n\d+\.\s.*?(?=\n|$)',
        '',
        text
    )

    text = re.sub(
        r'Constitution\s*\([^)]+\)\s*Amendment[^.]*\.',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'Ins\.[^.]*\.',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'Subs\.[^.]*\.',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'Omitted by[^.]*\.',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()