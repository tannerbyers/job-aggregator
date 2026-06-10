from enum import Enum


class RemoteType(str, Enum):
    REMOTE_US = "remote_us"
    REMOTE_OTHER = "remote_other"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"
