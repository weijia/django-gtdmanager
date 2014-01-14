from django.db import models
from django.core.exceptions import ValidationError
    
class ItemManager(models.Manager):
    def convertTo(self, cls, item):
        """
        Converts unresolved Item class instance to class cls extending Item
        @return: converted item
        Modified from code in https://code.djangoproject.com/ticket/7623#comment:21
        """
        if not isinstance(item, Item) or item.status != Item.UNRESOLVED:
            raise RuntimeError("passed item is not unresolved Item")
        
        converted = cls(item_ptr_id=item.id)
        attrs = item.__dict__
        attrs.pop('status')
        converted.__dict__.update(attrs)
        converted.save()
        return converted

class Item(models.Model):
    UNRESOLVED = 'U'
    DELETED = 'D'
    COMPLETED = 'C'
    WAITING_FOR = 'W'
    SOMEDAY = 'S'
    REFERENCE = 'F'
    REMINDER = 'R'
    NEXT = 'N'
    PROJECT = 'P'
    
    STATUSES = (
        (UNRESOLVED, 'Unresolved'),
        (DELETED, 'Deleted'),
        (COMPLETED, 'Completed'),
        (WAITING_FOR, 'Waiting for'),
        (SOMEDAY, 'Someday/Maybe'),
        (REFERENCE, 'Reference'),
        (REMINDER, 'Reminder'),
        (NEXT, 'Next'),
        (PROJECT, 'Project'),
    )
    
    objects = ItemManager()
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=STATUSES, db_index=True)
    parent = models.ForeignKey('Project', blank=True, null=True)    
    createdAt = models.DateField(auto_now_add=True)
    lastChanged = models.DateTimeField(auto_now=True)
            
    def __init__(self, *args, **kwargs):
        kwargs['status'] = kwargs.get('status', self.UNRESOLVED)
        super(Item, self).__init__(*args, **kwargs)
        
    def __unicode__(self):
        return self.name;  

class Project(Item):
    def __init__(self, *args, **kwargs):
        kwargs['status'] = kwargs.get('status', self.PROJECT)
        super(Project, self).__init__(*args, **kwargs)
        
    def is_parent_of(self, child):
        if child.parent is None:
            return False

        if child.parent == self:
            return True
        
        return self.is_parent_of(child.parent)
    
    def clean_fields(self, exclude=None):
        super(Project, self).clean_fields(exclude)
        if self.is_parent_of(self.parent):
            raise ValidationError("%(parent)s parenting %(child)s creates circular project reference",
                      params={ 'parent': self.parent, 'child': self }
                  )