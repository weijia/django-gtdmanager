from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from gtdmanager.models import Item, Project, Context, Next, Reminder, init_models

"""
Models Tests
"""

class GtdManagerTestCase(TestCase):
    def _pre_setup(self):
        super(GtdManagerTestCase, self)._pre_setup()
        init_models()

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
        
    def test_circular_parents(self):
        p1 = Project.objects.create(name='parent1')
        p2 = Project.objects.create(name='parent2', parent = p1)
        p3 = Project.objects.create(name='parent3', parent = p2)
        with self.assertRaises(ValidationError):
            p1.parent = p3
            p1.clean_fields()

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

class ReminderTest(GtdManagerTestCase):
    
    def test_init(self):
        r = Reminder(name='doit')
        self.assertGreater(r.remind_at, timezone.now())
        self.assertItemsEqual(r.contexts.all(), (Context.objects.default_context(),))
