from .clang_format import ClangFormatCheck
from .clang_tidy import ClangTidyCheck
from .include_guard import IncludeGuardCheck

CLASSES = [
    ClangFormatCheck,
    ClangTidyCheck,
    IncludeGuardCheck
]

NAMES = [c.name for c in CLASSES]
