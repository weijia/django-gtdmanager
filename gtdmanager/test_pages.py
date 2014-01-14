from django.test import TestCase, Client
from gtdmanager.models import Item
from django.core.urlresolvers import reverse

"""
Test pages funcionality
"""

class InboxTest(TestCase):
    def test_page_working(self):
        client = Client()
        response = client.get(reverse('gtdmanager:inbox'))
        self.assertEqual(response.status_code, 200)

    def test_delete_item(self):
        item = Item(name='item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:inbox_delete_item', args=(item.id,)))
        self.assertRedirects(response, reverse('gtdmanager:inbox'))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.DELETED)
        
    def test_delete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:inbox_delete_item', args=(15,)))
        self.assertEqual(response.status_code, 404)
        
    def test_complete_item(self):
        item = Item(name='completed item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:inbox_complete_item', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.COMPLETED)
        
    def test_complete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:inbox_complete_item', args=(15,)))
        self.assertEqual(response.status_code, 404)
        
    def test_reference_item(self):
        item = Item(name='reference')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:inbox_reference_item', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.REFERENCE)
        
    def test_reference_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:inbox_reference_item', args=(15,)))
        self.assertEqual(response.status_code, 404)
    
    def test_someday_item(self):
        item = Item(name='maybe')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:inbox_someday_item', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.SOMEDAY)
        
    def test_someday_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:inbox_someday_item', args=(15,)))
        self.assertEqual(response.status_code, 404)
    
    def test_wait_item(self):
        item = Item(name='waiting for Xmas')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:inbox_wait_item', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.WAITING_FOR)
        
    def test_wait_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:inbox_wait_item', args=(15,)))
        self.assertEqual(response.status_code, 404)