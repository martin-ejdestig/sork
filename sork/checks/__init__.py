from .clang_format import ClangFormatCheck
from .clang_tidy import ClangTidyCheck
from .include_guard import IncludeGuardCheck
from .license_header import LicenseHeaderCheck

CLASSES = [
    ClangFormatCheck,
    ClangTidyCheck,
    IncludeGuardCheck,
    LicenseHeaderCheck
]

NAMES = [c.name for c in CLASSES]
