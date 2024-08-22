from typing import Dict, List
from pydantic import BaseModel


class SocialNetUpdate(BaseModel):
    social_net: List[Dict[str, str]]

class BirthDateUpdate(BaseModel):
    fechaNacimiento: str