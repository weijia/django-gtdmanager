from django.test import TestCase
from gtdmanager.models import Item, Project

class ItemTest(TestCase):
    def test_item(self):
        expected_name = 'some name'
        item = Item.objects.create(name=expected_name)
        self.assertEqual(item.name, expected_name)
        self.assertEqual(item.status, Item.UNRESOLVED)
    
class ProjectTest(TestCase):
    def test_init(self):
        expected_name = 'some name'
        p = Project.objects.create(name=expected_name)
        self.assertEqual(p.name, expected_name)
        self.assertEqual(p.status, Item.PROJECT)