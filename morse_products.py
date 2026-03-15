from jsonschema import validate, ValidationError
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
import math

MAX_STRING_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_MANUFACTURER_LENGTH = 100
MIN_VOLUME_ML = 0.1
MAX_VOLUME_ML = 10000.0
MIN_ALCOHOL = 0.0
MAX_ALCOHOL = 20.0
MIN_RATING = 1
MAX_RATING = 5

morse_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": MAX_NAME_LENGTH,
            "pattern": r"^[\w\s\-]+$"
        },
        "berry_type": {
            "type": "string",
            "enum": ["cranberry", "lingonberry", "blueberry", "raspberry", "sea_buckthorn", "other"],
            "maxLength": 20
        },
        "volume_ml": {
            "type": "number",
            "exclusiveMinimum": 0,
            "minimum": MIN_VOLUME_ML,
            "maximum": MAX_VOLUME_ML
        },
        "has_sugar": {"type": "boolean"},
        "alcohol_percent": {
            "type": "number",
            "minimum": MIN_ALCOHOL,
            "maximum": MAX_ALCOHOL
        },
        "manufacturer": {
            "type": "string",
            "maxLength": MAX_MANUFACTURER_LENGTH,
            "pattern": r"^[\w\s\-\.]+$"
        },
        "rating": {
            "type": "integer",
            "minimum": MIN_RATING,
            "maximum": MAX_RATING
        }
    },
    "required": ["name", "berry_type", "volume_ml", "has_sugar"],
    "additionalProperties": False
}


class MorseProductJsonSchema:
    def __init__(self, data: dict):
        try:
            self.validate_numeric_values(data)
            validate(instance=data, schema=morse_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid morse data: {e.message}")
        except (ValueError, OverflowError) as e:
            raise ValueError(f"Invalid numeric value: {e}")

        self.name = data['name']
        self.berry_type = data['berry_type']
        self.volume_ml = data['volume_ml']
        self.has_sugar = data['has_sugar']
        self.alcohol_percent = data.get('alcohol_percent', 0.0)
        self.manufacturer = data.get('manufacturer')
        self.rating = data.get('rating')

        self.validate_energy_kcal()

    def validate_numeric_values(self, data: dict):
        numeric_fields = ['volume_ml', 'alcohol_percent']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        raise ValueError(f"Field '{field}' cannot be NaN or Infinity")
                    if value == 0.0 and math.copysign(1.0, value) < 0:
                        raise ValueError(f"Field '{field}' cannot be negative zero")

    def validate_energy_kcal(self):
        energy = self.energy_kcal
        max_energy = MAX_VOLUME_ML * 0.4
        if energy < 0 or energy > max_energy:
            raise ValueError(f"Calculated energy_kcal {energy} is out of reasonable range")

    @property
    def energy_kcal(self) -> float:
        if self.has_sugar:
            return round(self.volume_ml * 0.4, 1)
        else:
            return round(self.volume_ml * 0.1, 1)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'berry_type': self.berry_type,
            'volume_ml': self.volume_ml,
            'has_sugar': self.has_sugar,
            'alcohol_percent': self.alcohol_percent,
            'manufacturer': self.manufacturer,
            'rating': self.rating
        }

    def update(self, new_data: dict):
        current = self.to_dict()
        current.update(new_data)
        self.validate_numeric_values(current)
        try:
            validate(instance=current, schema=morse_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid morse data after update: {e.message}")
        old_values = {k: getattr(self, k) for k in current if hasattr(self, k)}
        for k, v in current.items():
            if hasattr(self, k):
                setattr(self, k, v)
        try:
            self.validate_energy_kcal()
        except Exception:
            for k, v in old_values.items():
                setattr(self, k, v)
            raise


BerryType = Literal['cranberry', 'lingonberry', 'blueberry', 'raspberry', 'sea_buckthorn', 'other']


class MorseProductPydantic(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, pattern=r'^[\w\s\-]+$')
    berry_type: BerryType
    volume_ml: float = Field(gt=0, ge=MIN_VOLUME_ML, le=MAX_VOLUME_ML)
    has_sugar: bool
    alcohol_percent: Optional[float] = Field(default=0.0, ge=MIN_ALCOHOL, le=MAX_ALCOHOL)
    manufacturer: Optional[str] = Field(default=None, max_length=MAX_MANUFACTURER_LENGTH, pattern=r'^[\w\s\-\.]+$')
    rating: Optional[int] = Field(default=None, ge=MIN_RATING, le=MAX_RATING)

    model_config = {
        "extra": "forbid",
        "strict": True,
        "validate_default": True,
        "validate_assignment": True
    }

    def __init__(self, **data):
        self.validate_numeric_values(data)
        super().__init__(**data)

    @staticmethod
    def validate_numeric_values(data: dict):
        numeric_fields = ['volume_ml', 'alcohol_percent']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        raise ValueError(f"Field '{field}' cannot be NaN or Infinity")
                    if value == 0.0 and math.copysign(1.0, value) < 0:
                        raise ValueError(f"Field '{field}' cannot be negative zero")

    @property
    def energy_kcal(self) -> float:
        if self.has_sugar:
            return round(self.volume_ml * 0.4, 1)
        else:
            return round(self.volume_ml * 0.1, 1)

    @model_validator(mode='after')
    def validate_model(self):
        energy = self.energy_kcal
        max_energy = MAX_VOLUME_ML * 0.4
        if energy < 0 or energy > max_energy:
            raise ValueError(f"Calculated energy_kcal {energy} is out of reasonable range")
        return self

    def update(self, new_data: dict):
        for key, value in new_data.items():
            setattr(self, key, value)