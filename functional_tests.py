import time

from selenium import webdriver
import unittest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        try:
            self.browser.get('http://localhost:8000')
        except WebDriverException:
            pass

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        item_list = ["rabbit", "cute puppy"]
        for i, item in enumerate(item_list, start=1):
            input_box = self.browser.find_element_by_id('id_new_item')
            self.assertEqual(
                input_box.get_attribute('placeholder'),
                'Enter a to-do item'
            )

            input_box.send_keys(item)

            input_box.send_keys(Keys.ENTER)
            time.sleep(1)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')

        for i, item in enumerate(item_list, start=1):
            row = rows[i-1]
            self.assertTrue(
                row.text == str(i)+': '+item,
                "새 아이템이 추가되지 않았어요!\n %s" % row.text
            )


if __name__ == '__main__':
    unittest.main()
