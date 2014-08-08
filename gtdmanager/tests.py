from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from gtdmanager.models import Item, Project, Context, Next, Reminder, init_models
from gtdmanager.forms import ProjectForm

"""
Models Tests
"""

class GtdManagerTestCase(TestCase):
    def _pre_setup(self):
        super(GtdManagerTestCase, self)._pre_setup()
        init_models()

    def create_from_completed(self, cls):
        item = cls(name='task')
        item.complete()
        self.assertEqual(item.status, Item.COMPLETED)
        item_get = cls.objects.get(pk=item.id)
        self.assertEqual(item_get.status, Item.COMPLETED)

    def template_unfinished(self, cls, ok_status):
        items = []
        data = {'1': ok_status, '2': Item.COMPLETED, '3': Item.DELETED, '4':ok_status}
        for name, status in data.iteritems():
            item = cls(name=name)
            item.status = status
            item.save()
            items.append(item)
        expected = (items[0], items[3],)
        result = cls.objects.unfinished()
        self.assertItemsEqual(expected, result)

    def setupProject(self, p):
        Project(name='sub', parent=p).save()
        Next(name='nxt', parent=p).save()
        Reminder(name='r', parent=p).save()
        Item(name='wait', status=Item.WAITING_FOR, parent=p).save()
        Item(name='sm', status=Item.SOMEDAY, parent=p).save()
        Item(name='ref', status=Item.REFERENCE, parent=p).save()
        Item(name='compl', parent=p).complete()
        Item(name='dele', parent=p).gtddelete()

    def check_items_group(self, items, groupName, itemName, itemType):
        self.assertEqual(1, len(items[groupName]))
        self.assertEqual(itemName, items[groupName][0]['name'])
        self.assertEqual(dict(Item.STATUSES)[itemType], items[groupName][0]['status'])

    def check_project_json(self, items):
        self.check_items_group(items, 'subprojects', 'sub', Item.PROJECT)
        self.assertNotIn('items', items['subprojects'][0])
        self.check_items_group(items, 'nexts', 'nxt', Item.NEXT)
        self.check_items_group(items, 'reminders', 'r', Item.REMINDER)
        self.check_items_group(items, 'waiting', 'wait', Item.WAITING_FOR)
        self.check_items_group(items, 'somedays', 'sm', Item.SOMEDAY)
        self.check_items_group(items, 'references', 'ref', Item.REFERENCE)
        self.check_items_group(items, 'completed', 'compl', Item.COMPLETED)
        self.check_items_group(items, 'deleted', 'dele', Item.DELETED)

    def prepare_completed_deleted(self):
        item = Item(name='completed', status = Item.COMPLETED)
        item.save()
        item2 = Item(name='deleted', status = Item.DELETED)
        item2.save()
        return (item, item2)

class ItemTest(GtdManagerTestCase):
    def test_item(self):
        expected_name = 'some name'
        item = Item.objects.create(name=expected_name)
        self.assertEqual(item.name, expected_name)
        self.assertEqual(item.status, Item.UNRESOLVED)

    def test_has_short_id(self):
        """
        Tests whether Item class has some sort of short id (e.g. id field)
        that can be used for identifying in URLs
        """
        item = Item(name="item")
        item.save()
        self.assertTrue(item.id in (0,1))

    def test_create_from_completed(self):
        self.create_from_completed(Item)

    def test_unfinished(self):
        self.template_unfinished(Item, Item.UNRESOLVED)

    def test_complete(self):
        item = Item(name='compl')
        item.complete()
        self.assertEqual(Item.COMPLETED, item.status)

    def test_gtddelete(self):
        item = Item(name='del')
        item.gtddelete()
        self.assertEqual(Item.DELETED, item.status)

    def test_json_noparent(self):
        start = timezone.now()
        item = Item(name='it', description='desc', status=Item.REFERENCE)
        item.save()
        data = item.to_json()
        self.assertEqual(7, len(data))
        self.assertIn('id', data)
        self.assertEqual('it', data['name'])
        self.assertEqual('desc', data['description'])
        self.assertEqual('Reference', data['status'])
        self.assertIsNone(data['parent_id'])
        self.assertLessEqual(start.date(), data['createdAt'])
        self.assertLessEqual(start, data['lastChanged'])

    def _item_parent(self):
        p = Project(name='parent')
        p.save()
        item = Item(name='it', parent=p)
        item.save()
        return (p, item)

    def test_json_parent(self):
        p, item = self._item_parent()
        data = item.to_json()
        self.assertEqual(p.id, data['parent_id'])

    def test_json_parent2(self):
        p, item = self._item_parent()
        data = item.to_json(True)
        self.assertEqual(p.id, data['parent_id'])
        self.assertEqual(p.name, data['parent_name'])

class ProjectTest(GtdManagerTestCase):
    def test_init(self):
        expected_name = 'some name'
        p = Project(name=expected_name)
        self.assertEqual(p.name, expected_name)
        self.assertEqual(p.status, Item.PROJECT)

    def test_is_parent_simple(self):
        parent = Project(name='parent')
        child = Project(name='child', parent = parent)
        self.assertTrue(parent.is_parent_of(child))
        self.assertFalse(child.is_parent_of(parent))

    def test_is_parent_multiple(self):
        parent = Project(name='parent')
        child = Project(name='child', parent = parent)
        subchild = Project(name='subchild', parent = child)
        self.assertEqual(subchild.parent, child)
        self.assertTrue(parent.is_parent_of(subchild))
        self.assertFalse(subchild.is_parent_of(parent))

    def test_is_parent_multiple_disconnected(self):
        parent1 = Project(name='parent1')
        child1 = Project(name='child1', parent = parent1)
        parent2 = Project(name='parent2')
        child2 = Project(name='child2', parent = parent2)
        subchild2 = Project(name='subchild2', parent = child2)

        self.assertFalse(parent1.is_parent_of(parent2))
        self.assertFalse(parent1.is_parent_of(child2))
        self.assertFalse(parent1.is_parent_of(subchild2))
        self.assertFalse(child1.is_parent_of(parent2))
        self.assertFalse(child1.is_parent_of(child2))
        self.assertFalse(child1.is_parent_of(subchild2))
        self.assertFalse(subchild2.is_parent_of(parent1))
        self.assertFalse(subchild2.is_parent_of(child1))

    def test_is_parent_none(self):
        p = Project(name='parent1')
        self.assertFalse(p.is_parent_of(None))

    def test_circular_parents(self):
        p1 = Project(name='parent1')
        p2 = Project(name='parent2', parent = p1)
        p3 = Project(name='parent3', parent = p2)
        with self.assertRaises(ValidationError):
            p1.parent = p3
            p1.clean_fields()

    def test_parenting_self_form_validation(self):
        p = Project(name='parent')
        p.save()
        postdata = {'name': 'test', 'parent': '27', 'description': ''}
        form = ProjectForm(postdata, instance=p)
        # foreign key is not updated, so form.instance.parent is still None,
        # we make check in ProjectForm
        self.assertFalse(form.is_valid())

    def test_convert(self):
        item = Item(name='Tst')
        item.save()
        self.assertEqual(item.status, Item.UNRESOLVED)
        self.assertEqual(len(Item.objects.all()), 1)
        self.assertEqual(len(Project.objects.all()), 0)
        p = Item.objects.convertTo(Project, item)
        p.save()
        self.assertEqual(p.status, Item.PROJECT)
        self.assertEqual(len(Item.objects.all()), 1)
        self.assertEqual(len(Project.objects.all()), 1)

    def test_convert_nonitem(self):
        item = Project('proj')
        with self.assertRaises(RuntimeError):
            Item.objects.convertTo(Next, item)

    def test_create_from_completed(self):
        self.create_from_completed(Project)

    def test_unfinished(self):
        self.template_unfinished(Project, Item.PROJECT)

    def _prepare_with_child(self, cls):
        p = Project(name='p')
        p.save()
        i = cls(name='child', parent=p)
        i.save()
        self.assertTrue(p.is_parent_of(i))
        return (p, i)

    def _prepare_with_active_subproject(self):
        p, sub = self._prepare_with_child(Project)
        i = Item(name='item', parent = sub)
        i.save()
        return (p, sub, i)

    def test_complete_with_child(self):
        p, i = self._prepare_with_child(Item)
        p.complete()
        i = Item.objects.get(pk=i.id)
        self.assertEqual(p.status, Item.COMPLETED)
        self.assertEqual(i.status, Item.COMPLETED)

    def test_gtddelete_with_child(self):
        p, i = self._prepare_with_child(Item)
        p.gtddelete()
        i = Item.objects.get(pk=i.id)
        self.assertEqual(p.status, Item.DELETED)
        self.assertEqual(i.status, Item.DELETED)

    def test_complete_with_subproject(self):
        p, sub, i = self._prepare_with_active_subproject()
        p.complete()
        sub = Item.objects.get(pk=sub.id)
        i = Item.objects.get(pk=i.id)
        self.assertEqual(p.status, Item.COMPLETED)
        self.assertEqual(sub.status, Item.COMPLETED)
        self.assertEqual(i.status, Item.COMPLETED)

    def test_gtddelete_with_subproject(self):
        p, sub, i = self._prepare_with_active_subproject()
        p.gtddelete()
        sub = Item.objects.get(pk=sub.id)
        i = Item.objects.get(pk=i.id)
        self.assertEqual(p.status, Item.DELETED)
        self.assertEqual(sub.status, Item.DELETED)
        self.assertEqual(i.status, Item.DELETED)

    def test_json(self):
        p = Project(name='parent')
        p.save()
        self.setupProject(p)
        data = p.to_json()
        self.assertNotIn('item_ptr_id', data)
        self.assertEqual(3, data['activeCount'])
        self.check_project_json(data['items'])

class ContextTest(GtdManagerTestCase):
    def check_consistency(self):
        self.assertEqual(len(Context.objects.filter(is_default=True)), 1)

    def test_default_always_exists(self):
        self.check_consistency()
        self.assertEquals(Context.objects.count(), 1)

    def test_create_new_default_context(self):
        new_def_context = Context(name='context5', is_default=True)
        new_def_context.save()
        self.assertEqual(new_def_context.is_default, True)
        self.assertEqual(Context.objects.default_context(), new_def_context)
        self.check_consistency()

    def test_disallow_delete_default(self):
        context = Context.objects.default_context()
        with self.assertRaises(RuntimeError):
            context.delete()

    def test_json(self):
        ctx = Context(name='wapa')
        ctx.save()
        data = ctx.to_json()
        self.assertEquals(3, len(data))
        self.assertFalse(data['is_default'])
        self.assertEqual('wapa', data['name'])
        self.assertIn('id', data)

class NextTest(GtdManagerTestCase):
    def test_status(self):
        item = Next(name='something')
        self.assertEqual(item.status, Item.NEXT)

    def test_create_no_context(self):
        item = Next(name='next2do')
        default_context = Context.objects.default_context()
        contexts = item.contexts.all()
        self.assertEqual(len(contexts),1)
        self.assertEqual(contexts[0], default_context)

    def test_init_context(self):
        ctx = Context.objects.default_context()
        item = Next(name='2d', context=ctx)
        self.assertItemsEqual([ctx], item.contexts.all())

    def test_init_multiple_contexts(self):
        context = Context(name='second')
        context.save()
        contexts = Context.objects.all()
        item = Next(name='2do', contexts = contexts)
        self.assertItemsEqual(contexts, item.contexts.all())

    def test_convert_save(self):
        item = Item(name='task')
        item.save()
        converted = Item.objects.convertTo(Next, item)
        self.assertIsInstance(converted, Next)
        converted.save()
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Next.objects.count(), 1)

    def test_new_default_context_not_added(self):
        task = Next(name='task')
        self.assertEqual(task.contexts.count(), 1)
        new_def = Context(name='newdef', is_default=True)
        new_def.save()
        self.assertEqual(task.contexts.count(), 1)
        task = Next.objects.get(pk=task.id)
        self.assertEqual(task.contexts.count(), 1)

    def delete_owning_setup(self):
        ctx = Context(name='ctx')
        ctx.save()
        new_def = Context(name='default', is_default=True)
        new_def.save()
        return (ctx, new_def)

    def test_delete_owning_single_context(self):
        context, new_def = self.delete_owning_setup()
        task = Next(name='task', context=context) #saved
        context.delete()
        self.assertEqual(Context.objects.count(), 2)
        self.assertItemsEqual(task.contexts.all(), (new_def,))

    def test_delete_owning_multiple_contexts(self):
        old_def = Context.objects.default_context()
        context, _ = self.delete_owning_setup()
        task = Next(name='task', contexts=(old_def, context)) #saved
        self.assertEqual(task.contexts.count(), 2)
        old_def = Context.objects.get(pk=old_def.id)
        old_def.delete()
        self.assertEqual(Context.objects.count(), 2)
        self.assertItemsEqual(task.contexts.all(), (context,))

    def test_create_from_completed(self):
        self.create_from_completed(Next)

    def test_unfinished(self):
        self.template_unfinished(Next, Item.NEXT)

    def test_json(self):
        nxt = Next(name='me')
        nxt.save()
        data = nxt.to_json()
        self.assertNotIn('item_ptr_id', data)
        def_ctx = Context.objects.default_context()
        self.assertEqual({def_ctx.id: def_ctx.name}, data['contexts']);

class ReminderTest(GtdManagerTestCase):

    def test_init(self):
        r = Reminder(name='doit')
        self.assertGreater(r.remind_at, timezone.now())
        self.assertItemsEqual(r.contexts.all(), (Context.objects.default_context(),))

    def test_create_from_completed(self):
        self.create_from_completed(Reminder)

    def test_unfinished(self):
        self.template_unfinished(Reminder, Item.REMINDER)

    def test_active(self):
        standard = Reminder(name='first')
        self.assertTrue(standard.active())
        standard.remind_at = timezone.now() + timedelta(days=1)
        self.assertFalse(standard.active())

    def test_json(self):
        rem = Next(name='rem')
        rem.save()
        data = rem.to_json()
        self.assertNotIn('item_ptr_id', data)
        def_ctx = Context.objects.default_context()
        self.assertEqual({def_ctx.id: def_ctx.name}, data['contexts']);
