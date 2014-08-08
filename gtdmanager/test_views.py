from django.test import TestCase, Client
from gtdmanager.models import Item, Next, Reminder, Project, Context
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from gtdmanager.tests import GtdManagerTestCase
import json

"""
Test pages funcionality
"""

class GtdViewTest(GtdManagerTestCase):

    def _getListData(self, page, entryName = 'listData'):
        response = Client().get(reverse(page))
        self.assertEqual(response.status_code, 200)
        return json.loads(response.context[entryName])

class InboxTest(GtdViewTest):
    def test_page_working(self):
        data = self._getListData('gtdmanager:inbox')
        self.assertEqual([], data)

    def test_btnName(self):
        response = Client().get(reverse('gtdmanager:inbox'))
        self.assertEqual("inbox", response.context["btnName"])

    def test_delete_item(self):
        item = Item(name='item')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        response = Client().get(reverse('gtdmanager:item_delete', args=(item.id,)))
        self.assertEqual(response.status_code, 200)
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
        response = Client().get(reverse('gtdmanager:item_complete', args=(15, )))
        self.assertEqual(response.status_code, 404)

class NextTest(GtdViewTest):

    def test_next(self):
        # autosaved
        task = Next(name='some task')
        data = self._getListData('gtdmanager:next', 'nexts')
        self.assertDictContainsSubset({"name": task.name}, data[0])

    def test_reminder(self):
        # autosaved
        rem = Reminder(name='some rem', remind_at=timezone.now())
        data = self._getListData('gtdmanager:next', 'reminders')
        self.assertDictContainsSubset({"name": rem.name}, data[0])

    def test_completed_next_filtered(self):
        Next(name='finished').complete()
        data = self._getListData('gtdmanager:next', 'nexts')
        self.assertEqual([], data)

    def test_completed_reminder_filtered(self):
        Reminder(name='completed').complete()
        data = self._getListData('gtdmanager:next', 'reminders')
        self.assertEqual([], data)

    def test_deleted_next_filtered(self):
        Next(name='deleted').gtddelete()
        data = self._getListData('gtdmanager:next', 'nexts')
        self.assertEqual([], data)

    def test_deleted_reminder_filtered(self):
        Reminder(name='deleted').gtddelete()
        data = self._getListData('gtdmanager:next', 'reminders')
        self.assertEqual([], data)

    def test_hide_unactive_reminders(self):
        #autosaved
        rem = Reminder(name='tada', remind_at=timezone.now() + timedelta(days=5))
        data = self._getListData('gtdmanager:next', 'reminders')
        self.assertEqual([], data)

    def create_context_item_with_two_contexts(self, cls, name):
        ctx = Context(name='other')
        ctx.save()
        item = cls(name=name)
        item.contexts.add(ctx)
        return item

    def test_no_multiple_nexts_when_multiple_contexts(self):
        n = self.create_context_item_with_two_contexts(Next, 'next')
        data = self._getListData('gtdmanager:next', 'nexts')
        self.assertEquals(1, len(data))

    def test_no_multiple_reminders_when_multiple_contexts(self):
        rem = self.create_context_item_with_two_contexts(Reminder, 'reminder')
        rem.remindAt = timezone.now()
        rem.save()
        data = self._getListData('gtdmanager:next', 'reminders')
        self.assertEquals(1, len(data))

class ProjectsTest(GtdViewTest):
    def test_working(self):
        p = Project(name='Proj')
        p.save()
        data = self._getListData('gtdmanager:projects')
        self.assertDictContainsSubset({"name": p.name}, data[0])

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

class ContextsTest(GtdViewTest):

    def test_working(self):
        defCtx = Context.objects.default_context()
        data = self._getListData('gtdmanager:contexts')
        self.assertDictContainsSubset({"name": defCtx.name}, data[0])

class WaitingTest(GtdViewTest):
    def test_working(self):
        item = Item(name='w8in4')
        item.status = Item.WAITING_FOR
        item.save()
        data = self._getListData('gtdmanager:waiting')
        self.assertDictContainsSubset({"name": item.name}, data[0])

    def test_hide_finished(self):
        self.prepare_completed_deleted()
        data = self._getListData('gtdmanager:waiting')
        self.assertEqual([], data)

class ReferencesTest(GtdViewTest):

    def test_working(self):
        item = Item(name='ref')
        item.status = Item.REFERENCE
        item.save()
        data = self._getListData('gtdmanager:references')
        self.assertDictContainsSubset({"name": item.name}, data[0])

    def test_hide_finished(self):
        self.prepare_completed_deleted()
        data = self._getListData('gtdmanager:references')
        self.assertEqual([], data)

class SomedayTest(GtdViewTest):
    def test_working(self):
        item = Item(name='ref')
        item.status = Item.SOMEDAY
        item.save()
        data = self._getListData('gtdmanager:someday')
        self.assertDictContainsSubset({"name": item.name}, data[0])

    def test_hide_finished(self):
        self.prepare_completed_deleted()
        data = self._getListData('gtdmanager:someday')
        self.assertEqual([], data)

class ArchiveTest(GtdViewTest):
    def test_working(self):
        completed, deleted = self.prepare_completed_deleted()
        data = self._getListData('gtdmanager:archive', 'completed')
        self.assertDictContainsSubset({"name": completed.name}, data[0])
        data = self._getListData('gtdmanager:archive', 'deleted')
        self.assertDictContainsSubset({"name": deleted.name}, data[0])

class TicklerTest(GtdViewTest):
    def test_tomorrow(self):
        r = Reminder(name='rem', remind_at = timezone.now() + timedelta(days=1))
        r.save()
        data = self._getListData('gtdmanager:tickler', 'tomorrows')
        self.assertDictContainsSubset({"name": r.name}, data[0])

    def test_futures(self):
        r = Reminder(name='rem', remind_at = timezone.now() + timedelta(days=10))
        r.save()
        data = self._getListData('gtdmanager:tickler', 'futures')
        self.assertDictContainsSubset({"name": r.name}, data[0])

    def test_this_week(self):
        r = Reminder(name='rem', remind_at = timezone.now() + timedelta(days=2))
        r.save()
        section = "futures" if timezone.now().isoweekday() > 5 else "this_week" # > 5 means Saturday or Sunday
        data = self._getListData('gtdmanager:tickler', section)
        self.assertDictContainsSubset({"name": r.name}, data[0])

    def test_completed_deleted(self):
        Reminder(name='compl', remind_at = timezone.now() + timedelta(days=7)).complete()
        Reminder(name='del', remind_at = timezone.now() + timedelta(days=7)).delete()
        data = self._getListData('gtdmanager:tickler', 'futures')
        self.assertEquals([], data)
