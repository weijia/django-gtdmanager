from django.db import models

class ItemManager(models.Manager):
    pass
    
class Item(models.Model):
    UNRESOLVED = 'U'
    DELETED = 'D'
    WAITING_FOR = 'W'
    SOMEDAY_MAYBE = 'S'
    REFERENCE = 'F'
    REMINDER = 'R'
    NEXT = 'N'
    PROJECT = 'P'
    
    STATUSES = (
        (UNRESOLVED, 'Unresolved'),
        (DELETED, 'Deleted'),
        (WAITING_FOR, 'Waiting for'),
        (SOMEDAY_MAYBE, 'Someday/Maybe'),
        (REFERENCE, 'Reference'),
        (REMINDER, 'Reminder'),
        (NEXT, 'Next'),
        (PROJECT, 'Project'),
    )
    
    objects = ItemManager()
    name = models.CharField(max_length=64, primary_key=True)
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