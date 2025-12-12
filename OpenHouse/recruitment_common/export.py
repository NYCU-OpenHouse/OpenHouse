import re

def sanitize_sheet_name(name: str) -> str:
    name = '' if name is None else str(name)
    name = re.sub(r'[\[\]\:\*\?\/\\]', '_', name)
    name = name.strip()
    if not name:
        name = 'Sheet'
    return name[:31]