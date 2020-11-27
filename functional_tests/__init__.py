import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

from django.test import LiveServerTestCase


class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        try:
            self.browser.get(self.live_server_url)
        except WebDriverException:
            pass

        self.check_title()
        item_list = ["Buy peacock feathers", "Use peacock feathers to make a fly'"]
        self.input_items(item_list)
        self.check_items_in_rows(item_list)

    def check_title(self):
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

    def input_items(self, item_list):
        for i, item in enumerate(item_list, start=1):
            input_box = self.browser.find_element_by_id('id_new_item')
            input_box.send_keys(item)
            input_box.send_keys(Keys.ENTER)
            time.sleep(0.5)

    def check_items_in_rows(self, item_list):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        for i, item in enumerate(item_list, start=1):
            row = rows[i - 1]
            real = row.text
            expected = str(i) + ': ' + item
            error_format = "새 아이템이 추가되지 않았어요!\n expected: %s\n real: %s"
            self.assertTrue(
                real == expected,
                error_format % (expected, real)
            )