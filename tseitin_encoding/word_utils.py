def is_whitespace(c):
    return ord(c) == 9 or ord(c) == 10 or ord(c) == 13 or ord(c) == 32

def is_printable(c):
    return ord(c) >= 128 or (ord(c) > 32 and ord(c) < 126)

def is_digit(c):
    return ord(c) >= 48 and ord(c) <= 57

def is_letter(c):
    return (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122)
