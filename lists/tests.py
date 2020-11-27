from django.test import TestCase
from lists.models import Item


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>To-Do lists</title>', html)
        self.assertTrue(html.strip().endswith('</html>'))

    def test_can_save_a_POST_request(self):
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertIn('A new list item', response.content.decode())


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        text_list = [
            'The first (ever) list item',
            'Item the second'
        ]
        for n_text in text_list:
            n_item = Item(text=n_text)
            n_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        for n_item, expected in zip(saved_items, text_list):
            self.assertEqual(n_item.text, expected)
