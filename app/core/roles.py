from typing import List


class Roles:
    # accreditation, checker, launch, swag, information
    ACCREDITATION = "accreditation"
    CHECKER = "checker"
    LAUNCH = "launch"
    SWAG = "swag"
    INFORMATION = "information"

    @staticmethod
    def get_roles() -> List[str]:
        return [Roles.ACCREDITATION, Roles.CHECKER, Roles.LAUNCH, Roles.SWAG, Roles.INFORMATION]