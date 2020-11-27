from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, timeout=5)

    def tearDown(self):
        self.browser.quit()

    def check_title(self):
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

    def input_items(self, item_list):
        for i, item in enumerate(item_list, start=1):
            self.wait.until(
                EC.presence_of_element_located((By.ID, 'id_new_item'))
            )
            input_box = self.browser.find_element_by_id('id_new_item')
            input_box.send_keys(item)
            input_box.send_keys(Keys.ENTER)

    def check_items_in_rows(self, item_list):
        self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_list_table'))
        )
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

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        item_list = ['Buy peacock feathers']
        self.input_items(item_list)
        self.check_items_in_rows(item_list)

        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        self.reboot_browser()

        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)

        francis_item_list = ['Buy milk']
        self.input_items(francis_item_list)
        self.check_items_in_rows(francis_item_list)

        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)

    def reboot_browser(self):
        self.browser.quit()
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, timeout=5)

