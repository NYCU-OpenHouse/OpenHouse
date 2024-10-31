""" This module contains the views helpers for the recruit and rdss app. """

# ======================== public view =======================
def change_website_start_with_http(website: str) -> str:
    """ This function will return url with https."""
    if not website.startswith('http'):
        website = 'https://' + website
    return website
