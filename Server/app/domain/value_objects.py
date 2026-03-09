from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    """Email value object - immutable"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Invalid email: {self.value}")
    
    def _is_valid(self) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, self.value) is not None
    
    def __str__(self):
        return self.value

@dataclass(frozen=True)
class Role:
    """Role value object"""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    
    value: str
    
    def __post_init__(self):
        if self.value not in [self.ADMIN, self.MANAGER, self.EMPLOYEE]:
            raise ValueError(f"Invalid role: {self.value}")
    
    def is_admin(self) -> bool:
        return self.value == self.ADMIN
    
    def is_manager(self) -> bool:
        return self.value == self.MANAGER
    
    def is_employee(self) -> bool:
        return self.value == self.EMPLOYEE