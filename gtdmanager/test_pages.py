from django.test import TestCase, Client
from gtdmanager.models import Item
from django.core.urlresolvers import reverse
from gtdmanager.tests import GtdManagerTestCase

"""
Test pages funcionality
"""

class InboxTest(GtdManagerTestCase):
    def test_page_working(self):
        client = Client()
        response = client.get(reverse('gtdmanager:inbox'))
        self.assertEqual(response.status_code, 200)

    def test_delete_item(self):
        item = Item(name='item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_delete', args=(item.id,)))
        self.assertRedirects(response, reverse('gtdmanager:inbox'))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.DELETED)
        
    def test_delete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_delete', args=(15,)))
        self.assertEqual(response.status_code, 404)
        
    def test_complete_item(self):
        item = Item(name='completed item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_complete', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.COMPLETED)
        
    def test_complete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_complete', args=(15,)))
        self.assertEqual(response.status_code, 404)
        
    def test_reference_item(self):
        item = Item(name='reference')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_reference', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.REFERENCE)
        
    def test_reference_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_reference', args=(15,)))
        self.assertEqual(response.status_code, 404)
    
    def test_someday_item(self):
        item = Item(name='maybe')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_someday', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.SOMEDAY)
        
    def test_someday_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_someday', args=(15,)))
        self.assertEqual(response.status_code, 404)
    
    def test_wait_item(self):
        item = Item(name='waiting for Xmas')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_wait', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.WAITING_FOR)
        
    def test_wait_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_wait', args=(15,)))
        self.assertEqual(response.status_code, 404)
        
    def test_item_to_project(self):
        item = Item(name='perfect project')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        Client().get(reverse('gtdmanager:item_to_project', args=(item.id,)))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.PROJECT)
        self.assertEqual(len(Item.objects.all()), 1)    # no new item not created
        
    def test_item_to_project_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_to_project', args=(15,)))
        self.assertEqual(response.status_code, 404)

class ContextsTest(GtdManagerTestCase):

    def test_working(self):
        response = Client().get(reverse('gtdmanager:contexts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['btnName'], 'manage')
        self.assertTrue('contexts', response.context)
        self.assertIn('form', response.context)
    
    def test_edit(self):
        response = Client().get(reverse('gtdmanager:context_edit', args=(1,)))
        self.assertEqual(response.status_code, 200)
