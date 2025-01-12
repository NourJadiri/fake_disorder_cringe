from typing import List, Dict


class Condition:
    def __init__(self,
                 name: str,
                 treatments: List[Dict],
                 severity: int,
                 ):
        self.name = name
        self.treatments = treatments
        self.severity = severity

    def __repr__(self):
        return f"Condition(name={self.name}, severity={self.severity}, treatments={self.treatments})"

    def to_dict(self):
        return {
            "name": self.name,
            "severity": self.severity,
            "treatments": self.treatments
        }

    @classmethod
    def from_json(cls, api_response: dict) -> 'Condition':
        return cls(
            name=api_response.get("entityName"),
            treatments=[treatment.get('entityName') for treatment in api_response.get("treatments")],
            severity=api_response.get("severity"),
        )