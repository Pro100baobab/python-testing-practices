from jsonschema import validate, ValidationError
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
import math

MAX_NAME_LENGTH = 100
MAX_COUNTRY_LENGTH = 100
COUNTRY_PATTERN = r'^[A-Za-zА-Яа-я\s\-]+$'
MAX_WEIGHT_GRAMS = 500000
MAX_PRICE_PER_KG = 10000
MAX_TOTAL_PRICE = 1_000_000
MIN_RATING = 1
MAX_RATING = 5

fish_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": MAX_NAME_LENGTH,
            "pattern": r"^[\w\s\-]+$"
        },
        "kind": {
            "type": "string",
            "enum": ["salmon", "cod", "carp", "perch", "other"]
        },
        "is_fresh": {"type": "boolean"},
        "weight_grams": {
            "type": "number",
            "exclusiveMinimum": 0,
            "maximum": MAX_WEIGHT_GRAMS
        },
        "price_per_kg": {
            "type": "number",
            "exclusiveMinimum": 0,
            "maximum": MAX_PRICE_PER_KG
        },
        "country": {
            "type": "string",
            "maxLength": MAX_COUNTRY_LENGTH,
            "pattern": COUNTRY_PATTERN
        },
        "quality_rating": {
            "type": "integer",
            "minimum": MIN_RATING,
            "maximum": MAX_RATING
        }
    },
    "required": ["name", "kind", "is_fresh", "weight_grams", "price_per_kg"],
    "additionalProperties": False
}


class FishProductJsonSchema:
    def __init__(self, data: dict):
        self.validate_numeric_values(data)
        try:
            validate(instance=data, schema=fish_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid fish data: {e.message}")

        self.name = data['name']
        self.kind = data['kind']
        self.is_fresh = data['is_fresh']
        self.weight_grams = data['weight_grams']
        self.price_per_kg = data['price_per_kg']
        self.country = data.get('country')
        self.quality_rating = data.get('quality_rating')

        self.validate_total_price()

    def validate_numeric_values(self, data: dict):
        numeric_fields = ['weight_grams', 'price_per_kg']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, float):
                    if math.isnan(value):
                        raise ValueError(f"Field '{field}' cannot be NaN")
                    if math.isinf(value):
                        raise ValueError(f"Field '{field}' cannot be Infinity")
                    if value == 0.0 and math.copysign(1.0, value) < 0:
                        raise ValueError(f"Field '{field}' cannot be negative zero")

    def validate_total_price(self):
        total = self.total_price
        if total <= 0:
            raise ValueError(f"Total price must be positive, got {total}")
        if total > MAX_TOTAL_PRICE:
            raise ValueError(f"Total price {total} exceeds maximum allowed {MAX_TOTAL_PRICE}")

    @property
    def total_price(self) -> float:
        return (self.weight_grams / 1000.0) * self.price_per_kg

    def to_dict(self) -> dict:
        """Возвращает текущие данные в виде словаря."""
        return {
            'name': self.name,
            'kind': self.kind,
            'is_fresh': self.is_fresh,
            'weight_grams': self.weight_grams,
            'price_per_kg': self.price_per_kg,
            'country': self.country,
            'quality_rating': self.quality_rating
        }

    def update(self, new_data: dict):
        """Обновляет данные с валидацией."""
        current = self.to_dict()
        current.update(new_data)
        self.validate_numeric_values(current)
        try:
            validate(instance=current, schema=fish_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid fish data after update: {e.message}")
        # Временно обновляем атрибуты для проверки total_price
        old_values = {k: getattr(self, k) for k in current if hasattr(self, k)}
        for k, v in current.items():
            if hasattr(self, k):
                setattr(self, k, v)
        try:
            self.validate_total_price()
        except Exception:
            # Откат при ошибке
            for k, v in old_values.items():
                setattr(self, k, v)
            raise


FishKind = Literal['salmon', 'cod', 'carp', 'perch', 'other']


class FishProductPydantic(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH, pattern=r'^[\w\s\-]+$')
    kind: FishKind
    is_fresh: bool
    weight_grams: float = Field(gt=0, le=MAX_WEIGHT_GRAMS)
    price_per_kg: float = Field(gt=0, le=MAX_PRICE_PER_KG)
    country: Optional[str] = Field(default=None, max_length=MAX_COUNTRY_LENGTH, pattern=COUNTRY_PATTERN)
    quality_rating: Optional[int] = Field(default=None, ge=MIN_RATING, le=MAX_RATING)

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
        numeric_fields = ['weight_grams', 'price_per_kg']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, float):
                    if math.isnan(value):
                        raise ValueError(f"Field '{field}' cannot be NaN")
                    if math.isinf(value):
                        raise ValueError(f"Field '{field}' cannot be Infinity")
                    if value == 0.0 and math.copysign(1.0, value) < 0:
                        raise ValueError(f"Field '{field}' cannot be negative zero")

    def validate_total_price(self):
        total = self.total_price
        if total <= 0:
            raise ValueError(f"Total price must be positive, got {total}")
        if total > MAX_TOTAL_PRICE:
            raise ValueError(f"Total price {total} exceeds maximum allowed {MAX_TOTAL_PRICE}")

    @property
    def total_price(self) -> float:
        return (self.weight_grams / 1000.0) * self.price_per_kg

    @model_validator(mode='after')
    def validate_model(self):
        self.validate_total_price()
        return self

    def update(self, new_data: dict):
        """Обновляет несколько полей одновременно."""
        for key, value in new_data.items():
            setattr(self, key, value)