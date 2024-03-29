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
        item = cls(name='task') #autosaved
        item.status = Item.COMPLETED
        item.save()
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

class ProjectTest(GtdManagerTestCase):
    def test_init(self):
        expected_name = 'some name'
        p = Project.objects.create(name=expected_name)
        self.assertEqual(p.name, expected_name)
        self.assertEqual(p.status, Item.PROJECT)
        
    def test_is_parent_simple(self):
        parent = Project.objects.create(name='parent')
        child = Project.objects.create(name='child', parent = parent)
        self.assertTrue(parent.is_parent_of(child))
        self.assertFalse(child.is_parent_of(parent))
        
    def test_is_parent_multiple(self):
        parent = Project.objects.create(name='parent')
        child = Project.objects.create(name='child', parent = parent)
        subchild = Project.objects.create(name='subchild', parent = child)
        self.assertEqual(subchild.parent, child)
        self.assertTrue(parent.is_parent_of(subchild))
        self.assertFalse(subchild.is_parent_of(parent))
        
    def test_is_parent_multiple_disconnected(self):
        parent1 = Project.objects.create(name='parent1')
        child1 = Project.objects.create(name='child1', parent = parent1)
        parent2 = Project.objects.create(name='parent2')
        child2 = Project.objects.create(name='child2', parent = parent2)
        subchild2 = Project.objects.create(name='subchild2', parent = child2)

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
        p1 = Project.objects.create(name='parent1')
        p2 = Project.objects.create(name='parent2', parent = p1)
        p3 = Project.objects.create(name='parent3', parent = p2)
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
    
    def test_active_childs_item(self):
        p = Project(name='p')
        p.save()
        Item(name='compl', status=Item.COMPLETED, parent=p).save()
        Item(name='del', status=Item.DELETED, parent=p).save()
        Item(name='sm', status=Item.SOMEDAY, parent=p).save()
        Item(name='ref', status=Item.REFERENCE, parent=p).save()
        waiting = Item(name='wait', status=Item.WAITING_FOR, parent=p)
        waiting.save()
        reminder = Reminder(name='arem', parent=p)
        reminder.save()
        anext = Next(name='next', parent=p)
        anext.save()
        self.assertEqual(p.item_set.count(), 7)
        self.assertItemsEqual((waiting, anext, reminder), p.active_childs())

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

    def convert(self, with_save):
        item = Item(name='task')
        if (with_save):
            item.save()
        converted = Item.objects.convertTo(Next, item)
        self.assertIsInstance(converted, Next)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Next.objects.count(), 1)

    def test_convert_save(self):
        self.convert(True)
    
    def test_convert_no_save(self):
        self.convert(False)

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