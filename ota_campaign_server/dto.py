from dataclasses import dataclass, fields


@dataclass(frozen=True)
class RolloutDTO:
    device_ids: list[str]
    package_version: str
    package_name: str

    @classmethod
    def from_json(cls, json_data):
        json_data = dict(json_data)

        json_keys = set(json_data.keys())
        dataclass_fields = set([field.name for field in fields(cls)])

        if dataclass_fields - json_keys:
            raise KeyError(f'Following keys are missing {dataclass_fields - json_keys}')

        return cls(**json_data)
