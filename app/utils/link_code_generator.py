import secrets
import string

ALPHABET = string.ascii_uppercase + string.digits


def generate_code(
    min_length: int = 5,
    max_length: int = 5,
) -> str:
    length = secrets.randbelow(max_length - min_length + 1) + min_length

    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def validate_codes(
    collection,
    codes: list[str],
    column: str = "code",
    other_conditions: dict | None = None,
) -> bool:
    if len(codes) != len(set(codes)):
        return False
    existing = collection.find_one(
        {column: {"$in": codes}, **(other_conditions or {})},
        {"_id": 1},
    )
    return existing is None


def generate_unique_codes(
    collection,
    quantity: int,
    column: str = "code",
    other_conditions: dict | None = None,
) -> list[str]:
    codes = [generate_code() for _ in range(quantity)]
    while True:
        seen = set()
        duplicates = set()
        for code in codes:
            if code in seen:
                duplicates.add(code)
            seen.add(code)
        for index, code in enumerate(codes):
            if code in duplicates:
                codes[index] = generate_code()
        if validate_codes(
            collection,
            codes,
            column=column,
            other_conditions=other_conditions,
        ):
            return codes
