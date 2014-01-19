from django.test import TestCase, Client
from gtdmanager.models import Item, Next, Reminder
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from gtdmanager.tests import GtdManagerTestCase

"""
Test pages funcionality
"""
def prepare_completed_finished():
    item = Item(name='completed')
    item.status = Item.COMPLETED
    item.save()
    item2 = Item(name='deleted')
    item2.status = Item.DELETED
    item2.save()

class InboxTest(GtdManagerTestCase):
    def test_page_working(self):
        client = Client()
        response = client.get(reverse('gtdmanager:inbox'))
        self.assertEqual(response.status_code, 200)

    def test_delete_item(self):
        item = Item(name='item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_delete', args=(item.id, 'inbox')))
        self.assertRedirects(response, reverse('gtdmanager:inbox'))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.DELETED)
        
    def test_delete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_delete', args=(15, 'inbox')))
        self.assertEqual(response.status_code, 404)
        
    def test_complete_item(self):
        item = Item(name='completed item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_complete', args=(item.id, 'inbox')))
        item = Item.objects.get(id=item.id)
        self.assertEqual(item.status, Item.COMPLETED)
        
    def test_complete_item_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_complete', args=(15, 'inbox')))
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
        self.assertEqual(len(Item.objects.all()), 1)  # no new item not created
        
    def test_item_to_project_nonexisting(self):
        response = Client().get(reverse('gtdmanager:item_to_project', args=(15,)))
        self.assertEqual(response.status_code, 404)

    def template_cancel(self, cls, class_url):
        item = Item(name='item')
        item.save()
        client = Client()
        #convert to next
        response = client.get(reverse('gtdmanager:'+class_url+'_edit', args=(item.id, 'inbox')))
        self.assertEqual(response.status_code, 200)
        converted = cls.objects.get(pk=item.id)
        self.assertEqual(converted.name, item.name)
        #cancel
        response = client.get(reverse('gtdmanager:'+class_url+'_to_item', args=(converted.id, 'inbox')))
        self.assertRedirects(response, reverse('gtdmanager:inbox'))
        self.assertEqual(cls.objects.count(), 0)
        item = Item.objects.get(pk=item.id)
        self.assertEqual(converted.name, item.name)

    def test_cancel_next(self):
        self.template_cancel(Next, 'next')

    def test_cancel_reminder(self):
        self.template_cancel(Reminder, 'reminder')

class NextTest(GtdManagerTestCase):
    
    def test_simple(self):
        # both autosaved
        task = Next(name='some task')
        rem = Reminder(name='some rem', remind_at=timezone.now())
        response = Client().get(reverse('gtdmanager:next'))
        self.assertEquals(response.status_code, 200)
        self.assertItemsEqual((task,), response.context['nexts'])
        self.assertItemsEqual((rem,), response.context['reminders'])
    
    def test_finished_filtered(self):
        task1 = Next(name='finished')
        task1.status = Item.COMPLETED
        task1.save()
        task2 = Reminder(name='deleted')
        task2.status = Item.DELETED
        task2.save()
        response = Client().get(reverse('gtdmanager:next'))
        self.assertItemsEqual((), response.context['nexts'])
        self.assertItemsEqual((), response.context['reminders'])

    def test_hide_unactive_reminders(self):
        rem = Reminder(name='tada')
        rem.remind_at = timezone.now() + timedelta(days=5)
        rem.save()
        response = Client().get(reverse('gtdmanager:next'))
        self.assertItemsEqual((), response.context['reminders'])

class ContextsTest(GtdManagerTestCase):

    def test_working(self):
        response = Client().get(reverse('gtdmanager:contexts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['btnName'], 'manage')
        self.assertTrue('contexts', response.context)
        self.assertIn('form', response.context)
    
    def test_edit(self):
        prepare_completed_finished()
        response = Client().get(reverse('gtdmanager:context_edit', args=(1,)))
        self.assertEqual(response.status_code, 200)

class WaitingTest(GtdManagerTestCase):
    def test_working(self):
        item = Item(name='w8in4')
        item.status = Item.WAITING_FOR
        item.save()
        response = Client().get(reverse('gtdmanager:waiting'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((item,), response.context['items'])

    def test_hide_finished(self):
        prepare_completed_finished()
        response = Client().get(reverse('gtdmanager:waiting'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['items'])


class ReferencesTest(GtdManagerTestCase):
    def test_working(self):
        item = Item(name='ref')
        item.status = Item.REFERENCE
        item.save()
        response = Client().get(reverse('gtdmanager:references'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((item,), response.context['items'])

    def test_hide_finished(self):
        prepare_completed_finished()
        response = Client().get(reverse('gtdmanager:references'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['items'])