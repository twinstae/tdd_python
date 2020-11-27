from django.test import TestCase
from lists.models import Item, List


class HomePageTest(TestCase):

    def test_only_saves_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        a_list = List()
        a_list.save()

        text_list = [
            'The first (ever) list item',
            'Item the second'
        ]
        for n_text in text_list:
            n_item = Item(text=n_text, list=a_list)
            n_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, a_list)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        for n_item, expected in zip(saved_items, text_list):
            self.assertEqual(n_item.text, expected)
            self.assertEqual(n_item.list, a_list)


class ListViewTest(TestCase):

    def test_displays_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='itemey 1', list=list_)
        Item.objects.create(text='itemey 2', list=list_)

        response = self.client.get('/lists/the-only-list-in-the-world')

        self.assertContains(response, 'itemey 1', msg_prefix=response.content.decode())
        self.assertContains(response, 'itemey 2')

    def test_uses_list_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world')
        self.assertTemplateUsed(response, 'lists/list.html')
        return response


class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertRedirects(response, '/lists/the-only-list-in-the-world')
