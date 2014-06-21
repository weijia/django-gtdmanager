from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from gtdmanager.tests import GtdManagerTestCase
from gtdmanager.models import Item, Context, Reminder, Next, Project
import json
from django.utils import timezone
from datetime import datetime, timedelta
from dajaxice.core import dajaxice_config
from django.utils.dateparse import parse_date

def createParent(name):
    p = Project(name=name)
    p.save()
    return p

class AjaxTestBase(GtdManagerTestCase):
    def checkModel(self, cls, data, parent):
        item = cls.objects.get(name=data['name'])
        self.assertEqual(data['name'], item.name)
        self.assertEqual(data['description'], item.description)
        self.assertEqual(data['status'], dict(Item.STATUSES)[item.status])
        if parent:
            self.assertEqual(parent, item.parent)
        return item

    def checkContext(self, ctx, data, shouldBeDefault):
        self.assertEqual(ctx.id, data['id'])
        self.assertEqual(ctx.name, data['name'])
        self.assertEqual(ctx.is_default, data['is_default'])
        self.assertEqual(shouldBeDefault, ctx.is_default)

    def checkResponse(self, response, data_field = 'data'):
        self.assertEqual(200, response.status_code)
        ret = json.loads(response.content)
        self.assertTrue(ret["success"])
        self.assertIn(data_field, ret)
        return ret[data_field]

class CreateTest(AjaxTestBase):

    def template_test_create_item(self, parentName = None):
        parent = None if parentName is None else createParent(parentName)
        data = {"name": 'item25', "description": "test desc"}
        if parent:
            data["parent"] = parent.id
        data = self.checkResponse(Client().post(reverse('gtdmanager:item_create'), data))
        self.checkModel(Item, data, parent)

    def test_create_item(self):
        self.template_test_create_item()

    def test_create_item_parent(self):
        self.template_test_create_item('folder')

    def template_create_reminder(self, parentName = None):
        parent = None if parentName is None else createParent(parentName)
        ctx = Context.objects.default_context()
        t = timezone.localtime(timezone.now() + timedelta(minutes=25))
        s = t.strftime("%Y-%m-%d %H:%M:%S")
        data = {"name": 'rem', "description": "default", "contexts": [ctx.id], "remind_at": s}
        if parent:
            data["parent"] = parent.id
        data = self.checkResponse(Client().post(reverse('gtdmanager:reminder_create'), data))
        rem = self.checkModel(Reminder, data, parent)
        timeDB = timezone.localtime(rem.remind_at).strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(s, timeDB)
        self.assertItemsEqual([ctx], rem.contexts.all())

    def test_create_reminder(self):
        self.template_create_reminder()

    def test_create_reminder_parent(self):
        self.template_create_reminder('proj')

    def template_create_next(self, parentName = None):
        parent = None if parentName is None else createParent(parentName)
        ctx = Context.objects.default_context()
        data = {"name": 'nxt', "description": "some","contexts": [ctx.id]}
        if parent:
            data["parent"] = parent.id
        data = self.checkResponse(Client().post(reverse('gtdmanager:next_create'), data))
        nxt = self.checkModel(Next, data, parent)
        self.assertItemsEqual([ctx], nxt.contexts.all())

    def test_create_next(self):
        self.template_create_next()

    def test_create_next_parent(self):
        self.template_create_next('tomcat')

    def template_create_project(self, parentName = None):
        parent = None if parentName is None else createParent(parentName)
        data = {"name": 'proj', "description": "best ever"}
        if parent:
            data["parent"] = parent.id
        data = self.checkResponse(Client().post(reverse('gtdmanager:project_create'), data))
        p = self.checkModel(Project, data, parent)

    def test_create_project(self):
        self.template_create_project()

    def test_create_subproject(self):
        self.template_create_project('parent')

    def test_create_context(self):
        c_name = '@test'
        data = self.checkResponse(Client().post(reverse('gtdmanager:context_create'), {"name": c_name}))
        ctx = Context.objects.get(name=data['name'])
        self.checkContext(ctx, data, False)

    def test_create_default_context(self):
        c_name = 'default'
        data = self.checkResponse(Client().post(
            reverse('gtdmanager:context_create'), {"name": c_name, "is_default": True}))
        ctx = Context.objects.get(name=data['name'])
        self.checkContext(ctx, data, True)

class UpdateTest(AjaxTestBase):

    def test_update_item(self):
        # status cannot be changed
        old = Item(name='howow', description='klakla', # status=Item.WAITING_FOR,
                   parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        data = {"name": 'item25', "description": "test desc", #"status": Item.SOMEDAY,
                "parent": p2.id}

        data = self.checkResponse(
            Client().post(reverse('gtdmanager:item_update', kwargs={"item_id": old.id}), data)
        )
        self.checkModel(Item, data, p2)

    def test_update_project(self):
        old = Project(name='proj', description='ultimate', parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        data = {"name": 'betterProj', "description": "", "parent": p2.id}

        data = self.checkResponse(
            Client().post(reverse('gtdmanager:project_update', kwargs={"item_id": old.id}), data)
        )
        self.checkModel(Project, data, p2)

    def test_update_next(self):
        old = Next(name='nxt', description='', parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        new_ctx = Context(name='neverwhere')
        new_ctx.save()
        data = {"name": 'Do me now', "description": "TODO", "parent": p2.id, "contexts": [new_ctx.id]}

        data = self.checkResponse(
            Client().post(reverse('gtdmanager:next_update', kwargs={"item_id": old.id}), data)
        )
        nxt = self.checkModel(Next, data, p2)
        self.assertItemsEqual([new_ctx], nxt.contexts.all())

    def test_update_reminder(self):
        # reminder with default reminder time, context and no parent project
        old = Reminder(name='rrr', description='apla')
        new_parent = createParent('other')
        new_ctx = Context(name='@nowhere')
        new_ctx.save()
        t = timezone.localtime(timezone.now() + timedelta(minutes=125))
        s = t.strftime("%Y-%m-%d %H:%M:%S")
        data = {"name": 'rem', "description": "default", "remind_at": s,
                "contexts": [new_ctx.id], "parent": new_parent.id}

        data = self.checkResponse(
            Client().post(reverse('gtdmanager:reminder_update', kwargs={"item_id": old.id}), data)
        )
        rem = self.checkModel(Reminder, data, new_parent)
        timeDB = timezone.localtime(rem.remind_at).strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(s, timeDB)
        self.assertItemsEqual([new_ctx], rem.contexts.all())

    def test_update_context(self):
        old = Context.objects.default_context()
        data = {"name": 'newname'}
        data = self.checkResponse(
            Client().post(reverse('gtdmanager:context_update', kwargs={"item_id": old.id}), data)
        )
        new = Context.objects.get(name=data['name'])
        self.checkContext(new, data, True)

class DeleteCompleteBaseTest(AjaxTestBase):
    def base_template(self, cls, name, prefix, postfix, finalStatus):
        item = cls(name=name)
        item.save()
        self.assertEquals(1, cls.objects.count())

        response = Client().get(
            reverse('gtdmanager:%s_%s' % (prefix, postfix), kwargs={"item_id": item.id}) )
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        self.assertEquals(finalStatus, cls.objects.get(name=name).status)

    # will be overloaded in child classes
    def exec_template(self, cls, name, prefix):
        pass

    def test_item(self):
        self.exec_template(Item, 'itm', 'item')

    def test_project(self):
        self.exec_template(Project, 'proj', 'project')

    def test_next(self):
        self.exec_template(Next, 'nxt', 'item')

    def test_reminder(self):
        self.exec_template(Reminder, 'rem', 'item')

class DeleteTest(DeleteCompleteBaseTest):

    def exec_template(self, cls, name, prefix):
        self.base_template(cls, name, prefix, 'delete', Item.DELETED)

    def test_delete_context(self):
        def_ctx = Context.objects.default_context()
        ctx = Context(name='other')
        ctx.save()
        self.assertEquals(2, Context.objects.count())

        response = Client().get(reverse('gtdmanager:context_delete', kwargs={"item_id": ctx.id}))
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))
        self.assertEquals(1, Context.objects.count())
        self.assertEquals(def_ctx, Context.objects.first())

class CompleteTest(DeleteCompleteBaseTest):

    def exec_template(self, cls, name, prefix):
        self.base_template(cls, name, prefix, 'complete', Item.COMPLETED)


class GetTestBase(AjaxTestBase):

    def setup_model(self, cls, name, view, postSaveCallback = None):
        item = cls(name=name)
        item.save()
        if postSaveCallback:
            postSaveCallback(item)

        #url = '/%sgtdmanager.[view]/?argv={"item_id":%d}' % (dajaxice_config.dajaxice_url[1:], item.id)
        data = self.checkResponse(
            Client().get(reverse(view, kwargs={"item_id": item.id})),
            self.Meta.data_field
        )
        return (item, data)

class GetFormTest(GetTestBase):

    class Meta:
        data_field = 'form_html'

    def check_minimal_fields(self, html, actionURL):
        self.assertIn('csrfmiddlewaretoken', html)
        self.assertIn('Name', html)
        self.assertIn('Submit', html)
        self.assertIn('action="%s"' % actionURL, html)

    def check_base_fields(self, html, actionURL):
        self.check_minimal_fields(html, actionURL)
        self.assertIn('Description', html)
        self.assertIn('Parent', html)

    def test_getform_item(self):
        name = 'test_get'
        item, html = self.setup_model(Item, name, 'gtdmanager:item_form')
        actionURL = reverse('gtdmanager:item_update', kwargs={"item_id": item.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_project(self):
        name = 'test_name'
        p, html = self.setup_model(Project, name, 'gtdmanager:project_form')
        actionURL = reverse('gtdmanager:project_update', kwargs={"item_id": p.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_next(self):
        name = 'nxt_NaMe'
        nxt, html = self.setup_model(Next, name, 'gtdmanager:next_form')
        actionURL = reverse('gtdmanager:next_update', kwargs={"item_id": nxt.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_reminder(self):
        name = 'rmd'
        r, html = self.setup_model(Reminder, name, 'gtdmanager:reminder_form')
        actionURL = reverse('gtdmanager:reminder_update', kwargs={"item_id": r.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_context(self):
        name = 'newCtx'
        ctx, html = self.setup_model(Context, name, 'gtdmanager:context_form')
        actionURL = reverse('gtdmanager:context_update', kwargs={"item_id": ctx.id})
        self.check_minimal_fields(html, actionURL)
        self.assertIn('value="'+ctx.name+'"', html)

class GetTest(GetTestBase):

    class Meta():
        data_field = 'data'

    def formatDjangoDatetime(self, o):
        """
        Returns same format for date-aware datetime as DjangoJsonSerializer
        """
        r = o.isoformat()
        if o.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        return r

    def check_model(self, instance, data):
        self.assertEqual(data['name'], instance.name)
        self.assertEqual(data['description'], instance.description)
        aware = timezone.localtime(instance.lastChanged)
        self.assertEqual(data['lastChanged'], self.formatDjangoDatetime(aware))
        self.assertEqual(data['parent_id'], instance.parent_id)
        self.assertEqual(parse_date(data['createdAt']), instance.createdAt)

    def test_get_item(self):
        item, dct = self.setup_model(Item, 'test_get', 'gtdmanager:item_get')
        self.check_model(item, dct)
        self.assertDictContainsSubset({'status' : 'Unresolved'}, dct)

    def test_get_reminder(self):
        r, dct = self.setup_model(Reminder, 'rmd', 'gtdmanager:reminder_get')
        self.check_model(r, dct)
        aware = timezone.localtime(r.remind_at)
        self.assertEqual(dct['remind_at'], self.formatDjangoDatetime(aware))
        def_ctx = Context.objects.default_context()
        self.assertEqual([def_ctx.id], dct['contexts']);

    def test_get_next(self):
        r, dct = self.setup_model(Next, 'nxt', 'gtdmanager:next_get')
        self.check_model(r, dct)
        def_ctx = Context.objects.default_context()
        self.assertEqual([def_ctx.id], dct['contexts']);

    def test_get_context(self):
        ctx, dct = self.setup_model(Context, 'newCtx', 'gtdmanager:context_get')
        self.assertEqual(False, dct['is_default'])
        self.assertEqual(ctx.name, dct['name'])
        self.assertEqual(ctx.id, dct['id'])

    def test_get_project(self):
        p, dct = self.setup_model(Project, 'parent', 'gtdmanager:project_get', self.setupProject)
        self.check_model(p, dct)
        self.check_project_json(dct['items'])
