from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserEntity:
    id: Optional[int] = None
    name: str = ""
    username: str = ""
    role: str = "employee"
    department_id: Optional[int] = None
    created_at: Optional[datetime] = None

    def is_manager(self) -> bool:
        return self.role == "manager"

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_employee(self) -> bool:
        return self.role == "employee"
