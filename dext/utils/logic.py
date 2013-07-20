# coding: utf-8


def normalize_email(email):
    dog_index = email.rfind('@')
    return email[:dog_index] + email[dog_index:].lower()
