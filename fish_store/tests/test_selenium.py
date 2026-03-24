import os
import unittest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from catalog.models import FishProduct


class CatalogSeleniumTests(StaticLiveServerTestCase):
    """Selenium-тесты для каталога"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_driver_path = os.path.join(os.path.dirname(__file__), '..', 'chromedriver-win64/chromedriver.exe')
        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        cls.driver = webdriver.Chrome(service=service, options=options)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.product = FishProduct.objects.create(
            name='Тестовая рыба',
            kind='salmon',
            is_fresh=True,
            weight_grams=1000,
            price_per_kg=500,
            country='Россия',
            quality_rating=5
        )

    def test_navigate_to_about_page(self):
        """Проверка перехода со страницы списка на страницу 'О сервисе'"""
        self.driver.get(self.live_server_url)

        # Ждём загрузки главной страницы
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "О сервисе"))
        )

        # Находим ссылку и кликаем
        about_link = self.driver.find_element(By.LINK_TEXT, "О сервисе")
        about_link.click()

        # Проверяем, что на новой странице есть заголовок с текстом "О нашем каталоге"
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        heading = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertIn("О нашем каталоге", heading.text)

    def test_detail_page_has_heading(self):
        """Проверка, что на странице детального описания товара есть заголовок (тег h1)"""
        url = self.live_server_url + f'/product/{self.product.pk}/'
        self.driver.get(url)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        heading = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertEqual(heading.text, self.product.name)
