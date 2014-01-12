from django.test import TestCase
from django.core.exceptions import ValidationError
from gtdmanager.models import Item, Project

class ItemTest(TestCase):
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
        
class ProjectTest(TestCase):
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
