import unittest
from fish_products import (
    FishProductJsonSchema, FishProductPydantic,
    MAX_NAME_LENGTH, MAX_COUNTRY_LENGTH, MAX_WEIGHT_GRAMS,
    MAX_PRICE_PER_KG, MIN_RATING, MAX_RATING
)
from pydantic import ValidationError as PydanticValidationError


class TestFishProductJsonSchema(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Семга атлантическая',
            'kind': 'salmon',
            'is_fresh': True,
            'weight_grams': 1500.5,
            'price_per_kg': 1200.0,
            'country': 'Норвегия',
            'quality_rating': 5
        }

    def test_valid_full(self):
        fish = FishProductJsonSchema(self.valid_data)
        self.assertEqual(fish.name, 'Семга атлантическая')
        self.assertEqual(fish.kind, 'salmon')
        self.assertTrue(fish.is_fresh)
        self.assertEqual(fish.weight_grams, 1500.5)
        self.assertEqual(fish.price_per_kg, 1200.0)
        self.assertEqual(fish.country, 'Норвегия')
        self.assertEqual(fish.quality_rating, 5)
        expected_total = (1500.5 / 1000) * 1200.0
        self.assertAlmostEqual(fish.total_price, expected_total)

    def test_valid_without_optional(self):
        data = self.valid_data.copy()
        del data['country']
        del data['quality_rating']
        fish = FishProductJsonSchema(data)
        self.assertIsNone(fish.country)
        self.assertIsNone(fish.quality_rating)

    def test_missing_required_fields(self):
        required = ['name', 'kind', 'is_fresh', 'weight_grams', 'price_per_kg']
        for field in required:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                del data[field]
                with self.assertRaises(ValueError):
                    FishProductJsonSchema(data)

    def test_name_validation(self):
        with self.subTest("empty name"):
            data = self.valid_data.copy()
            data['name'] = ''
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("too long name"):
            data = self.valid_data.copy()
            data['name'] = 'A' * (MAX_NAME_LENGTH + 1)
            with self.assertRaises(ValueError) as ctx:
                FishProductJsonSchema(data)
            self.assertIn("is too long", str(ctx.exception))

        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['name'] = 'Семга @#$%'
            with self.assertRaises(ValueError) as ctx:
                FishProductJsonSchema(data)
            self.assertIn("does not match", str(ctx.exception))

    def test_invalid_kind(self):
        data = self.valid_data.copy()
        data['kind'] = 'trout'
        with self.assertRaises(ValueError):
            FishProductJsonSchema(data)

    def test_weight_validation(self):
        with self.subTest("negative weight"):
            data = self.valid_data.copy()
            data['weight_grams'] = -100
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("zero weight"):
            data = self.valid_data.copy()
            data['weight_grams'] = 0
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("weight too large"):
            data = self.valid_data.copy()
            data['weight_grams'] = MAX_WEIGHT_GRAMS + 1
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("weight string"):
            data = self.valid_data.copy()
            data['weight_grams'] = 'one thousand'
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

    def test_weight_special_floats(self):
        specials = [
            (float('nan'), "NaN"),
            (float('inf'), "Infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['weight_grams'] = value
                with self.assertRaises(ValueError) as ctx:
                    FishProductJsonSchema(data)
                self.assertIn(msg, str(ctx.exception))

    def test_price_validation(self):
        with self.subTest("negative price"):
            data = self.valid_data.copy()
            data['price_per_kg'] = -10.0
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("zero price"):
            data = self.valid_data.copy()
            data['price_per_kg'] = 0
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("price too high"):
            data = self.valid_data.copy()
            data['price_per_kg'] = MAX_PRICE_PER_KG + 1
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

    def test_price_special_floats(self):
        specials = [
            (float('nan'), "NaN"),
            (float('inf'), "Infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['price_per_kg'] = value
                with self.assertRaises(ValueError) as ctx:
                    FishProductJsonSchema(data)
                self.assertIn(msg, str(ctx.exception))

    def test_is_fresh_not_bool(self):
        data = self.valid_data.copy()
        data['is_fresh'] = 'yes'
        with self.assertRaises(ValueError):
            FishProductJsonSchema(data)

    def test_country_validation(self):
        with self.subTest("too long"):
            data = self.valid_data.copy()
            data['country'] = 'A' * (MAX_COUNTRY_LENGTH + 1)
            with self.assertRaises(ValueError):
                FishProductJsonSchema(data)

        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['country'] = 'Norway@123'
            with self.assertRaises(ValueError) as ctx:
                FishProductJsonSchema(data)
            self.assertIn("does not match", str(ctx.exception))

    def test_rating_validation(self):
        for rating in [MIN_RATING - 1, MAX_RATING + 1]:
            with self.subTest(rating=rating):
                data = self.valid_data.copy()
                data['quality_rating'] = rating
                with self.assertRaises(ValueError):
                    FishProductJsonSchema(data)

    def test_extra_field(self):
        data = self.valid_data.copy()
        data['extra'] = 'field'
        with self.assertRaises(ValueError) as ctx:
            FishProductJsonSchema(data)
        self.assertIn("Additional properties are not allowed", str(ctx.exception))

    def test_update_valid(self):
        fish = FishProductJsonSchema(self.valid_data)
        fish.update({'weight_grams': 2000.0, 'price_per_kg': 1300.0})
        self.assertEqual(fish.weight_grams, 2000.0)
        self.assertEqual(fish.price_per_kg, 1300.0)
        expected_total = (2000.0 / 1000) * 1300.0
        self.assertAlmostEqual(fish.total_price, expected_total)

    def test_total_price_positive_check(self):
        fish = FishProductJsonSchema(self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            fish.update({'weight_grams': 0.0})
        self.assertIn("less than or equal to the minimum of 0", str(ctx.exception))

    def test_total_price_positive_check_negative(self):
        fish = FishProductJsonSchema(self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            fish.update({'price_per_kg': -10.0})
        self.assertIn("less than or equal to the minimum of 0", str(ctx.exception))

    def test_update_invalid(self):
        fish = FishProductJsonSchema(self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            fish.update({'weight_grams': -100.0})
        self.assertIn("minimum", str(ctx.exception))

    def test_total_price_exceeds_max(self):
        data = self.valid_data.copy()
        data['weight_grams'] = MAX_WEIGHT_GRAMS
        data['price_per_kg'] = MAX_PRICE_PER_KG
        with self.assertRaises(ValueError) as ctx:
            FishProductJsonSchema(data)
        self.assertIn("exceeds maximum allowed", str(ctx.exception))

    def test_total_price_calculation_precision(self):
        fish = FishProductJsonSchema(self.valid_data)
        expected = (1500.5 / 1000.0) * 1200.0
        self.assertAlmostEqual(fish.total_price, expected, places=6)


class TestFishProductPydantic(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Семга атлантическая',
            'kind': 'salmon',
            'is_fresh': True,
            'weight_grams': 1500.5,
            'price_per_kg': 1200.0,
            'country': 'Норвегия',
            'quality_rating': 5
        }

    def test_valid_full(self):
        fish = FishProductPydantic(**self.valid_data)
        self.assertEqual(fish.name, 'Семга атлантическая')
        self.assertEqual(fish.kind, 'salmon')
        self.assertTrue(fish.is_fresh)
        self.assertEqual(fish.weight_grams, 1500.5)
        self.assertEqual(fish.price_per_kg, 1200.0)
        self.assertEqual(fish.country, 'Норвегия')
        self.assertEqual(fish.quality_rating, 5)
        expected_total = (1500.5 / 1000) * 1200.0
        self.assertAlmostEqual(fish.total_price, expected_total)

    def test_valid_without_optional(self):
        data = self.valid_data.copy()
        del data['country']
        del data['quality_rating']
        fish = FishProductPydantic(**data)
        self.assertIsNone(fish.country)
        self.assertIsNone(fish.quality_rating)

    def test_missing_required_fields(self):
        required = ['name', 'kind', 'is_fresh', 'weight_grams', 'price_per_kg']
        for field in required:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                del data[field]
                with self.assertRaises(PydanticValidationError):
                    FishProductPydantic(**data)

    def test_name_validation(self):
        with self.subTest("empty name"):
            data = self.valid_data.copy()
            data['name'] = ''
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("too long name"):
            data = self.valid_data.copy()
            data['name'] = 'A' * (MAX_NAME_LENGTH + 1)
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['name'] = 'Семга @#$%'
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)

    def test_invalid_kind(self):
        data = self.valid_data.copy()
        data['kind'] = 'trout'
        with self.assertRaises(PydanticValidationError):
            FishProductPydantic(**data)

    def test_weight_validation(self):
        with self.subTest("negative weight"):
            data = self.valid_data.copy()
            data['weight_grams'] = -100
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("zero weight"):
            data = self.valid_data.copy()
            data['weight_grams'] = 0
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("weight too large"):
            data = self.valid_data.copy()
            data['weight_grams'] = MAX_WEIGHT_GRAMS + 1
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("weight string"):
            data = self.valid_data.copy()
            data['weight_grams'] = '1500'
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)

    def test_weight_special_floats(self):
        specials = [
            (float('nan'), "NaN"),
            (float('inf'), "Infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['weight_grams'] = value
                with self.assertRaises(ValueError) as ctx:
                    FishProductPydantic(**data)
                self.assertIn(msg, str(ctx.exception))

    def test_price_validation(self):
        with self.subTest("negative price"):
            data = self.valid_data.copy()
            data['price_per_kg'] = -10.0
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("zero price"):
            data = self.valid_data.copy()
            data['price_per_kg'] = 0
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("price too high"):
            data = self.valid_data.copy()
            data['price_per_kg'] = MAX_PRICE_PER_KG + 1
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)

    def test_price_special_floats(self):
        specials = [
            (float('nan'), "NaN"),
            (float('inf'), "Infinity"),
            (-0.0, "negative zero")
        ]
        for value, msg in specials:
            with self.subTest(value=value):
                data = self.valid_data.copy()
                data['price_per_kg'] = value
                with self.assertRaises(ValueError) as ctx:
                    FishProductPydantic(**data)
                self.assertIn(msg, str(ctx.exception))

    def test_is_fresh_not_bool(self):
        data = self.valid_data.copy()
        data['is_fresh'] = 'yes'
        with self.assertRaises(PydanticValidationError):
            FishProductPydantic(**data)

    def test_country_validation(self):
        with self.subTest("too long"):
            data = self.valid_data.copy()
            data['country'] = 'A' * (MAX_COUNTRY_LENGTH + 1)
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)
        with self.subTest("invalid chars"):
            data = self.valid_data.copy()
            data['country'] = 'Norway@123'
            with self.assertRaises(PydanticValidationError):
                FishProductPydantic(**data)

    def test_rating_validation(self):
        for rating in [MIN_RATING - 1, MAX_RATING + 1]:
            with self.subTest(rating=rating):
                data = self.valid_data.copy()
                data['quality_rating'] = rating
                with self.assertRaises(PydanticValidationError):
                    FishProductPydantic(**data)

    def test_extra_field(self):
        data = self.valid_data.copy()
        data['extra'] = 'field'
        with self.assertRaises(PydanticValidationError):
            FishProductPydantic(**data)

    def test_assignment_validation(self):
        fish = FishProductPydantic(**self.valid_data)
        with self.assertRaises(ValueError):
            fish.weight_grams = 0.0

    def test_total_price_positive_check(self):
        fish = FishProductPydantic(**self.valid_data)
        with self.assertRaises(ValueError) as ctx:
            fish.weight_grams = 0.0


    def test_total_price_exceeds_max(self):
        data = self.valid_data.copy()
        data['weight_grams'] = MAX_WEIGHT_GRAMS
        data['price_per_kg'] = MAX_PRICE_PER_KG
        with self.assertRaises(ValueError) as ctx:
            FishProductPydantic(**data)
        self.assertIn("exceeds maximum allowed", str(ctx.exception))

    def test_total_price_calculation_precision(self):
        fish = FishProductPydantic(**self.valid_data)
        expected = (1500.5 / 1000.0) * 1200.0
        self.assertAlmostEqual(fish.total_price, expected, places=6)


if __name__ == '__main__':
    unittest.main()
