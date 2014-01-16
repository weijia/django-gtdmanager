from django.db import models
from django.core.exceptions import ValidationError

class ContextManager(models.Manager):
    
    def default_context(self):
        return self.filter(is_default=True).first()

class Context(models.Model):    
    default_name = 'Everywhere'
    
    name = models.CharField(max_length=64, unique=True)
    is_default = models.BooleanField(default=False)
    
    objects = ContextManager()
    
    def __unicode__(self):
        return self.name
    
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.is_default:
            default = Context.objects.default_context()
            if default is not None:     # in model init
                default.is_default = False
                default.save(update_fields=['is_default'])
        super(Context, self).save(force_insert, force_update, using, update_fields)

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
        kwargs['status'] = self.PROJECT
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

"""
Post init procedures, should be called in test setup
Should be solved via signalS, but they aren't working well in Django 1.6
"""
def init_models():
    # Ensure at least one Context instance with default true
    if Context.objects.count() == 0:
       default_context = Context(name=Context.default_name, is_default=True)
       default_context.save()

try:
    init_models()
except:
    print "Models init failed. Ignore if performing syncdb"