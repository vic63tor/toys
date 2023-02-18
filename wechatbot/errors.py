import logging

class MismatchError(Exception):
    def __init__(self, message):
        super().__init__(message)
        print(f"ERROR: {message}")