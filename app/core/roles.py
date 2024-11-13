from typing import List


class Roles:
    # accreditation, checker, launch, swag, information
    ACCREDITATION = "accreditation"
    CHECKER = "checker"
    LAUNCH = "launch"
    SWAG = "swag"
    INFORMATION = "information"
    SPECIAL_POINT = "special_point"

    @staticmethod
    def get_roles() -> List[str]:
        return [Roles.ACCREDITATION, Roles.CHECKER, Roles.LAUNCH, Roles.SWAG, Roles.INFORMATION, Roles.SPECIAL_POINT]