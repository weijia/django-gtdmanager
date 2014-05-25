from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date, time

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
            if default is not None and default is not self:  # in model init
                default.is_default = False
                default.save(update_fields=['is_default'])
        super(Context, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None):
        if self.is_default:
            raise RuntimeError("Cannot delete default context")
        super(Context, self).delete(using=using)

        # get nexts with no context and assign them the default one
        default = Context.objects.default_context()
        for item in Next.objects.filter(contexts__isnull=True):
            item.contexts.add(default)

class ItemManager(models.Manager):
    def convertTo(self, cls, item):
        """
        Converts unresolved Item class instance to class cls extending Item
        @return: converted item
        Modified from code in https://code.djangoproject.com/ticket/7623#comment:21
        """
        if not isinstance(item, Item) or item.status != Item.UNRESOLVED:
            raise RuntimeError("passed item is not unresolved Item")
        
        attrs = item.__dict__
        attrs.pop('status')
        converted = cls(item_ptr_id=item.id)
        converted.__dict__.update(attrs)
        return converted

    def unfinished(self):
        excluded = (Item.COMPLETED, Item.DELETED)
        return self.exclude(status__in=excluded) 

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
        set_status = kwargs.pop('status', self.UNRESOLVED)
        super(Item, self).__init__(*args, **kwargs)
        if not self.status:
            self.status = set_status
        
    def __unicode__(self):
        return self.name;

    def complete(self):
        self.status = Item.COMPLETED
        self.save()
    
    def gtddelete(self):
        self.status = Item.DELETED
        self.save()

class ContextsItem(Item):
    """
    Warning: due to containing ManyToManyField forcing at least one association,
    it is autosaved on creation
    """

    contexts = models.ManyToManyField(Context)
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        contextSet = []
        if 'context' in kwargs:
            contextSet.append(kwargs.pop('context'))
        if 'contexts' in kwargs:
            contextSet.extend(kwargs.pop('contexts'))
        instance = kwargs.pop('instance', None)

        super(ContextsItem, self).__init__(*args, **kwargs)
        
        if instance:
            self.__dict__.update(instance.__dict__)
        self.createdAt = timezone.now()  # next save would failed otherwise
        self.save()
        if contextSet:
            self.contexts.add(*contextSet)
        elif self.contexts.count() == 0:
            self.contexts.add(Context.objects.default_context())

class Next(ContextsItem):

    objects = ItemManager()

    def __init__(self, *args, **kwargs):
        kwargs['status'] = self.NEXT
        super(Next, self).__init__(*args, **kwargs)

class ReminderManager(ItemManager):
    def active(self):
        tomorrow = datetime.combine(date.today(), time()) + timedelta(days=1)
        tz = timezone.get_current_timezone()
        return self.unfinished().filter(remind_at__lt=tomorrow.replace(tzinfo=tz))

class Reminder(ContextsItem):

    remind_at = models.DateTimeField()
    
    objects = ReminderManager()

    def __init__(self, *args, **kwargs):
        kwargs['status'] = self.REMINDER
        if 'remind_at' not in kwargs:
            kwargs['remind_at'] = timezone.now() + timedelta(minutes=10) 
        super(Reminder, self).__init__(*args, **kwargs)
    
    def active(self):
        return self.remind_at.date() <= timezone.now().date()


class Project(Item):

    objects = ItemManager()

    def __init__(self, *args, **kwargs):
        kwargs['status'] = self.PROJECT
        super(Project, self).__init__(*args, **kwargs)

    def is_parent_of(self, child):
        if child is None or child.parent is None:
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

    def context_items(self, cls, unfinished_only = False):
        if (unfinished_only):
            return cls.objects.unfinished().filter(parent=self)
        else:
            return cls.objects.filter(parent=self)

    def nexts(self, unfinished_only = False):
        return self.context_items(Next, unfinished_only)

    def reminders(self, unfinished_only = False):
        return self.context_items(Reminder, unfinished_only)

    def subprojects(self, unfinished_only = False):
        return self.context_items(Project, unfinished_only)

    def active_childs(self):
        childs = list(self.item_set.filter(status=Item.WAITING_FOR))
        childs.extend(self.nexts(True))
        childs.extend(self.reminders(True))
        childs.extend([sub for sub in self.subprojects(True) if len(sub.active_childs()) > 0 ])
        return childs

    def complete(self):
        for p in self.subprojects(True):
            p.complete()

        for item in self.item_set.unfinished():
            item.complete()
        super(Project, self).complete()

    def gtddelete(self):
        for p in self.subprojects(True):
            p.gtddelete()

        for item in self.item_set.unfinished():
            item.gtddelete()
        super(Project, self).gtddelete()

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
