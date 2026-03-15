import unittest
import math
from morse_products import (
    MorseProductJsonSchema, MorseProductPydantic,
    MAX_NAME_LENGTH, MAX_MANUFACTURER_LENGTH,
    MIN_VOLUME_ML, MAX_VOLUME_ML,
    MIN_ALCOHOL, MAX_ALCOHOL,
    MIN_RATING, MAX_RATING
)
from pydantic import ValidationError as PydanticValidationError


class TestMorseProductJsonSchema(unittest.TestCase):
    """Тесты для JSON Schema подхода (MorseProductJsonSchema)"""

    def setUp(self):
        self.valid_data = {
            'name': 'Клюквенный морс',
            'berry_type': 'cranberry',
            'volume_ml': 500.0,
            'has_sugar': True,
            'alcohol_percent': 0.0,
            'manufacturer': 'Ягодка',
            'rating': 5
        }

    def test_valid_full(self):
        morse = MorseProductJsonSchema(self.valid_data)
        self.assertEqual(morse.name, 'Клюквенный морс')
        self.assertEqual(morse.berry_type, 'cranberry')
        self.assertEqual(morse.volume_ml, 500.0)
        self.assertTrue(morse.has_sugar)
        self.assertEqual(morse.alcohol_percent, 0.0)
        self.assertEqual(morse.manufacturer, 'Ягодка')
        self.assertEqual(morse.rating, 5)
        self.assertAlmostEqual(morse.energy_kcal, 500 * 0.4)

    def test_valid_without_optional(self):
        data = self.valid_data.copy()
        del data['alcohol_percent']
        del data['manufacturer']
        del data['rating']
        morse = MorseProductJsonSchema(data)
        self.assertEqual(morse.alcohol_percent, 0.0)
        self.assertIsNone(morse.manufacturer)
        self.assertIsNone(morse.rating)

    def test_missing_required_fields(self):
        required = ['name', 'berry_type', 'volume_ml', 'has_sugar']
        for field in required:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                del data[field]
                with self.assertRaises(ValueError):
                    MorseProductJsonSchema(data)

    def test_name_validation(self):
        with self.subTest("empty name"):
            data = self.valid_data.copy()
            data['name'] = ''
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("too long name"):
            data = self.valid_data.copy()
            data['name'] = 'A' * (MAX_NAME_LENGTH + 1)
            with self.assertRaises(ValueError) as ctx:
                MorseProductJsonSchema(data)
            self.assertIn("is too long", str(ctx.exception))
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['name'] = 'Клюквенный@#$%морс'
            with self.assertRaises(ValueError) as ctx:
                MorseProductJsonSchema(data)
            self.assertIn("does not match", str(ctx.exception))

    def test_invalid_berry_type(self):
        data = self.valid_data.copy()
        data['berry_type'] = 'strawberry'
        with self.assertRaises(ValueError):
            MorseProductJsonSchema(data)

    def test_volume_validation(self):
        with self.subTest("negative volume"):
            data = self.valid_data.copy()
            data['volume_ml'] = -100
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("zero volume"):
            data = self.valid_data.copy()
            data['volume_ml'] = 0
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("too small positive"):
            data = self.valid_data.copy()
            data['volume_ml'] = 0.01  # меньше MIN_VOLUME_ML = 0.1
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("too large"):
            data = self.valid_data.copy()
            data['volume_ml'] = MAX_VOLUME_ML + 1
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("string instead of number"):
            data = self.valid_data.copy()
            data['volume_ml'] = 'five hundred'
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)

    def test_volume_special_floats(self):
        specials = [
            (float('nan'), "nan"),
            (float('inf'), "infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['volume_ml'] = value
                with self.assertRaises(ValueError) as ctx:
                    MorseProductJsonSchema(data)
                self.assertIn(msg, str(ctx.exception).lower())

    def test_has_sugar_not_bool(self):
        data = self.valid_data.copy()
        data['has_sugar'] = 'yes'
        with self.assertRaises(ValueError):
            MorseProductJsonSchema(data)

    def test_alcohol_percent_validation(self):
        with self.subTest("negative"):
            data = self.valid_data.copy()
            data['alcohol_percent'] = -1.0
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("too high"):
            data = self.valid_data.copy()
            data['alcohol_percent'] = 25.0
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)

    def test_alcohol_percent_special_floats(self):
        specials = [
            (float('nan'), "nan"),
            (float('inf'), "infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['alcohol_percent'] = value
                with self.assertRaises(ValueError) as ctx:
                    MorseProductJsonSchema(data)
                self.assertIn(msg, str(ctx.exception).lower())

    def test_manufacturer_validation(self):
        with self.subTest("too long"):
            data = self.valid_data.copy()
            data['manufacturer'] = 'B' * (MAX_MANUFACTURER_LENGTH + 1)
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['manufacturer'] = 'Ягодка@#$%'
            with self.assertRaises(ValueError):
                MorseProductJsonSchema(data)

    def test_rating_validation(self):
        for rating in [MIN_RATING - 1, MAX_RATING + 1]:
            with self.subTest(rating=rating):
                data = self.valid_data.copy()
                data['rating'] = rating
                with self.assertRaises(ValueError):
                    MorseProductJsonSchema(data)

    def test_extra_field(self):
        data = self.valid_data.copy()
        data['extra'] = 'field'
        with self.assertRaises(ValueError) as ctx:
            MorseProductJsonSchema(data)
        self.assertIn("Additional properties are not allowed", str(ctx.exception))

    def test_energy_calculation_no_sugar(self):
        data = self.valid_data.copy()
        data['has_sugar'] = False
        data['volume_ml'] = 250.0
        morse = MorseProductJsonSchema(data)
        self.assertAlmostEqual(morse.energy_kcal, 250 * 0.1)

    def test_energy_kcal_rounding(self):
        data = self.valid_data.copy()
        data['volume_ml'] = 123.45
        morse = MorseProductJsonSchema(data)
        expected = round(123.45 * 0.4, 1)
        self.assertEqual(morse.energy_kcal, expected)

    def test_energy_kcal_out_of_range(self):
        """Проверка, что объём не может превышать максимальный"""
        data = self.valid_data.copy()
        data['volume_ml'] = MAX_VOLUME_ML
        data['has_sugar'] = True
        morse = MorseProductJsonSchema(data)
        with self.assertRaises(ValueError) as ctx:
            morse.update({'volume_ml': MAX_VOLUME_ML + 1000})
        self.assertIn("greater than the maximum", str(ctx.exception))

    def test_update_invalid(self):
        morse = MorseProductJsonSchema(self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            morse.update({'volume_ml': -100.0})
        self.assertIn("minimum", str(ctx.exception))

    def test_update_invalid(self):
        morse = MorseProductJsonSchema(self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            morse.update({'volume_ml': -100.0})
        self.assertIn("less than or equal to the minimum of 0", str(ctx.exception))


class TestMorseProductPydantic(unittest.TestCase):
    """Тесты для Pydantic подхода (MorseProductPydantic)"""

    def setUp(self):
        self.valid_data = {
            'name': 'Клюквенный морс',
            'berry_type': 'cranberry',
            'volume_ml': 500.0,
            'has_sugar': True,
            'alcohol_percent': 0.0,
            'manufacturer': 'Ягодка',
            'rating': 5
        }

    def test_valid_full(self):
        morse = MorseProductPydantic(**self.valid_data)
        self.assertEqual(morse.name, 'Клюквенный морс')
        self.assertEqual(morse.berry_type, 'cranberry')
        self.assertEqual(morse.volume_ml, 500.0)
        self.assertTrue(morse.has_sugar)
        self.assertEqual(morse.alcohol_percent, 0.0)
        self.assertEqual(morse.manufacturer, 'Ягодка')
        self.assertEqual(morse.rating, 5)
        self.assertAlmostEqual(morse.energy_kcal, 500 * 0.4)

    def test_valid_without_optional(self):
        data = self.valid_data.copy()
        del data['alcohol_percent']
        del data['manufacturer']
        del data['rating']
        morse = MorseProductPydantic(**data)
        self.assertEqual(morse.alcohol_percent, 0.0)
        self.assertIsNone(morse.manufacturer)
        self.assertIsNone(morse.rating)

    def test_missing_required_fields(self):
        required = ['name', 'berry_type', 'volume_ml', 'has_sugar']
        for field in required:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                del data[field]
                with self.assertRaises(PydanticValidationError):
                    MorseProductPydantic(**data)

    def test_name_validation(self):
        with self.subTest("empty name"):
            data = self.valid_data.copy()
            data['name'] = ''
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("too long name"):
            data = self.valid_data.copy()
            data['name'] = 'A' * (MAX_NAME_LENGTH + 1)
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['name'] = 'Клюквенный@#$%морс'
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)

    def test_invalid_berry_type(self):
        data = self.valid_data.copy()
        data['berry_type'] = 'strawberry'
        with self.assertRaises(PydanticValidationError):
            MorseProductPydantic(**data)

    def test_volume_validation(self):
        with self.subTest("negative volume"):
            data = self.valid_data.copy()
            data['volume_ml'] = -100
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("zero volume"):
            data = self.valid_data.copy()
            data['volume_ml'] = 0
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("too small positive"):
            data = self.valid_data.copy()
            data['volume_ml'] = 0.01
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("too large"):
            data = self.valid_data.copy()
            data['volume_ml'] = MAX_VOLUME_ML + 1
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("string instead of number"):
            data = self.valid_data.copy()
            data['volume_ml'] = 'five hundred'
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)

    def test_volume_special_floats(self):
        specials = [
            (float('nan'), "nan"),
            (float('inf'), "infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['volume_ml'] = value
                with self.assertRaises(ValueError) as ctx:
                    MorseProductPydantic(**data)
                self.assertIn(msg, str(ctx.exception).lower())

    def test_has_sugar_not_bool(self):
        data = self.valid_data.copy()
        data['has_sugar'] = 'yes'
        with self.assertRaises(PydanticValidationError):
            MorseProductPydantic(**data)

    def test_alcohol_percent_validation(self):
        with self.subTest("negative"):
            data = self.valid_data.copy()
            data['alcohol_percent'] = -1.0
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("too high"):
            data = self.valid_data.copy()
            data['alcohol_percent'] = 25.0
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)

    def test_alcohol_percent_special_floats(self):
        specials = [
            (float('nan'), "nan"),
            (float('inf'), "infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['alcohol_percent'] = value
                with self.assertRaises(ValueError) as ctx:
                    MorseProductPydantic(**data)
                self.assertIn(msg, str(ctx.exception).lower())

    def test_manufacturer_validation(self):
        with self.subTest("too long"):
            data = self.valid_data.copy()
            data['manufacturer'] = 'B' * (MAX_MANUFACTURER_LENGTH + 1)
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['manufacturer'] = 'Ягодка@#$%'
            with self.assertRaises(PydanticValidationError):
                MorseProductPydantic(**data)

    def test_rating_validation(self):
        for rating in [MIN_RATING - 1, MAX_RATING + 1]:
            with self.subTest(rating=rating):
                data = self.valid_data.copy()
                data['rating'] = rating
                with self.assertRaises(PydanticValidationError):
                    MorseProductPydantic(**data)

    def test_extra_field(self):
        data = self.valid_data.copy()
        data['extra'] = 'field'
        with self.assertRaises(PydanticValidationError):
            MorseProductPydantic(**data)

    def test_assignment_validation(self):
        morse = MorseProductPydantic(**self.valid_data)
        with self.assertRaises(ValueError):
            morse.volume_ml = 0.0

    def test_energy_calculation_no_sugar(self):
        data = self.valid_data.copy()
        data['has_sugar'] = False
        data['volume_ml'] = 250.0
        morse = MorseProductPydantic(**data)
        self.assertAlmostEqual(morse.energy_kcal, 250 * 0.1)

    def test_energy_kcal_rounding(self):
        data = self.valid_data.copy()
        data['volume_ml'] = 123.45
        morse = MorseProductPydantic(**data)
        expected = round(123.45 * 0.4, 1)
        self.assertEqual(morse.energy_kcal, expected)


if __name__ == '__main__':
    unittest.main()
