from django.test import TestCase, Client
from gtdmanager.models import Item, Next, Reminder, Project, Context
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from gtdmanager.tests import GtdManagerTestCase

"""
Test pages funcionality
"""
def prepare_completed_deleted():
    item = Item(name='completed', status = Item.COMPLETED)
    item.save()
    item2 = Item(name='deleted', status = Item.DELETED)
    item2.save()
    return (item, item2)

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
        # convert to next
        response = client.get(reverse('gtdmanager:' + class_url + '_edit', args=(item.id, 'inbox')))
        self.assertEqual(response.status_code, 200)
        converted = cls.objects.get(pk=item.id)
        self.assertEqual(converted.name, item.name)
        # cancel
        response = client.get(reverse('gtdmanager:' + class_url + '_to_item', args=(converted.id, 'inbox')))
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

    def create_nextItem_two_contexts(self, cls, name):
        ctx = Context(name='other')
        ctx.save()
        item = cls(name=name)
        item.contexts.add(ctx)
        return item

    def test_no_multiple_nexts_when_multiple_contexts(self):
        n = self.create_nextItem_two_contexts(Next, 'next')
        response = Client().get(reverse('gtdmanager:next'))
        self.assertItemsEqual((n,), response.context['nexts'])

    def test_no_multiple_reminders_when_multiple_contexts(self):
        rem = self.create_nextItem_two_contexts(Reminder, 'reminder')
        rem.remindAt = timezone.now()
        rem.save()
        response = Client().get(reverse('gtdmanager:next'))
        self.assertItemsEqual((rem,), response.context['reminders'])

class ProjectsTest(GtdManagerTestCase):
    def test_working(self):
        p = Project(name='Proj')
        p.save()
        response = Client().get(reverse('gtdmanager:projects'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['btnName'], 'projects')
        self.assertItemsEqual((p,), response.context['projects'])

    def test_edit(self):
        p = Project(name='p')
        p.save()
        response = Client().get(reverse('gtdmanager:project_edit', args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['title'], 'Edit project')
        self.assertEqual(response.context['edit'], True)

class ProjectDetailTest(GtdManagerTestCase):
    def test_working(self):
        p = Project(name='p')
        p.save()
        sub = Project(name='subproject', parent=p)
        sub.save()
        completed = Item(name='compl', status=Item.COMPLETED, parent=p)
        completed.save()
        deleted = Item(name='del', status=Item.DELETED, parent=p)
        deleted.save()
        someday = Item(name='sm', status=Item.SOMEDAY, parent=p)
        someday.save()
        reference = Item(name='ref', status=Item.REFERENCE, parent=p)
        reference.save()
        waiting = Item(name='wait', status=Item.WAITING_FOR, parent=p)
        waiting.save()
        reminder = Reminder(name='arem', parent=p)
        reminder.save()
        anext = Next(name='next', parent=p)
        anext.save()
        self.assertEqual(p.item_set.count(), 8)
        
        response = Client().get(reverse('gtdmanager:project_detail', args=(p.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.context['subprojects'], (sub,))
        self.assertItemsEqual(response.context['nexts'], (anext,))
        self.assertItemsEqual(response.context['reminders'], (reminder,))
        self.assertItemsEqual(response.context['waiting'], (waiting,))
        self.assertItemsEqual(response.context['somedays'], (someday,))
        self.assertItemsEqual(response.context['references'], (reference,))
        self.assertItemsEqual(response.context['completed'], (completed,))
        self.assertItemsEqual(response.context['deleted'], (deleted,))

class ContextsTest(GtdManagerTestCase):

    def test_working(self):
        response = Client().get(reverse('gtdmanager:contexts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['btnName'], 'manage')
        self.assertTrue('contexts', response.context)
        self.assertIn('form', response.context)

    def test_edit(self):
        prepare_completed_deleted()
        response = Client().get(reverse('gtdmanager:context_edit', args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['title'], 'Edit context')
        self.assertEqual(response.context['edit'], True)

class WaitingTest(GtdManagerTestCase):
    def test_working(self):
        item = Item(name='w8in4')
        item.status = Item.WAITING_FOR
        item.save()
        response = Client().get(reverse('gtdmanager:waiting'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((item,), response.context['items'])

    def test_hide_finished(self):
        prepare_completed_deleted()
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
        prepare_completed_deleted()
        response = Client().get(reverse('gtdmanager:references'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['items'])

class SomedayTest(GtdManagerTestCase):
    def test_working(self):
        item = Item(name='ref')
        item.status = Item.SOMEDAY
        item.save()
        response = Client().get(reverse('gtdmanager:someday'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((item,), response.context['items'])

    def test_hide_finished(self):
        prepare_completed_deleted()
        response = Client().get(reverse('gtdmanager:someday'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['items'])

class ArchiveTest(GtdManagerTestCase):
    def test_working(self):
        completed, deleted = prepare_completed_deleted()
        response = Client().get(reverse('gtdmanager:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((completed,), response.context['completed'])
        self.assertItemsEqual((deleted,), response.context['deleted'])

    def test_clean(self):
        prepare_completed_deleted()
        response = Client().get(reverse('gtdmanager:archive_clean'))
        self.assertRedirects(response, reverse('gtdmanager:archive'))
        response = Client().get(reverse('gtdmanager:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['completed'])
        self.assertItemsEqual((), response.context['deleted'])

class ArchiveTest(GtdManagerTestCase):
    def test_working(self):
        reminder = Reminder(name='rem', remind_at = timezone.now() + timedelta(days=1))
        reminder.save()
        reminder2 = Reminder(name='rem2', remind_at = timezone.now() + timedelta(days=2))
        reminder2.save()
        reminder3 = Reminder(name='rem3', remind_at = timezone.now() + timedelta(days=10))
        reminder3.save()
        response = Client().get(reverse('gtdmanager:tickler'))
        self.assertEqual(response.status_code, 200)
        tomorrows = [reminder,]
        this_week = []
        futures = [reminder3,]
        if timezone.now().isoweekday() > 5: #Saturday or Sunday
            futures.append(reminder2)
        else:
            this_week.append(reminder2)
        self.assertItemsEqual(tomorrows, response.context['tomorrows'])
        self.assertItemsEqual(this_week, response.context['this_week'])
        self.assertItemsEqual(futures, response.context['futures'])

    def test_completed_deleted(self):
        completed = Reminder(name='compl', remind_at = timezone.now() + timedelta(days=7))
        completed.complete()
        completed.save()
        deleted = Reminder(name='del', remind_at = timezone.now() + timedelta(days=7))
        deleted.complete()
        deleted.save()
        response = Client().get(reverse('gtdmanager:tickler'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual((), response.context['futures'])
