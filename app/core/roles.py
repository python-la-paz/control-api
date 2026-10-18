from typing import List


class Roles:
    # accreditation, checker, launch, swag, information
    ADMIN = "admin"
    ACCREDITATION = "accreditation"
    CHECKER = "checker"
    LAUNCH = "launch"
    SWAG = "swag"
    INFORMATION = "information"
    SPECIAL_POINT = "special_point"
    REVOCATION = "revocation"
    COMBO = "combo"

    @staticmethod
    def get_roles() -> List[str]:
        return [
            Roles.ADMIN,
            Roles.ACCREDITATION,
            Roles.CHECKER,
            Roles.LAUNCH,
            Roles.SWAG,
            Roles.INFORMATION,
            Roles.SPECIAL_POINT,
            Roles.REVOCATION,
            Roles.COMBO,
        ]
