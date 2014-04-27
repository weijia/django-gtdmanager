from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from gtdmanager.tests import GtdManagerTestCase
from gtdmanager.models import Item, Context, Reminder, Next, Project
import json
from django.utils import timezone
from datetime import datetime, timedelta
from dajaxice.core import dajaxice_config

def createParent(name):
    p = Project(name=name)
    p.save()
    return p

class AjaxTestBase(GtdManagerTestCase):
    def checkModel(self, cls, data, parent):
        item = cls.objects.get(name=data['name'])
        self.assertEqual(data['name'], item.name)
        self.assertEqual(data['description'], item.description)
        self.assertEqual(data.get('status', Item.UNRESOLVED), item.status)
        if parent:
            self.assertEqual(parent, item.parent)
        return item

class CreateTest(AjaxTestBase):

    def template_test_create_item(self, parentName = None):
        parent = None if parentName is None else createParent(parentName)
        data = {"name": 'item25', "description": "test desc"}
        if parent:
            data["parent"] = parent.id
        response = Client().post(reverse('gtdmanager:item_create'), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))
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
        response = Client().post(reverse('gtdmanager:reminder_create'), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.REMINDER;
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
        response = Client().post(reverse('gtdmanager:next_create'), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.NEXT;
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
        response = Client().post(reverse('gtdmanager:project_create'), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.PROJECT;
        p = self.checkModel(Project, data, parent)

    def test_create_project(self):
        self.template_create_project()

    def test_create_subproject(self):
        self.template_create_project('parent')

    def test_create_context(self):
        c_name = '@test'
        response = Client().post(reverse('gtdmanager:context_create'), {"name": c_name})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        ctx = Context.objects.get(name=c_name)
        self.assertEqual(c_name, ctx.name)
        self.assertFalse(ctx.is_default)

    def test_create_default_context(self):
        c_name = 'default'
        response = Client().post(
            reverse('gtdmanager:context_create'), {"name": c_name, "is_default": True})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        ctx = Context.objects.get(name=c_name)
        self.assertEqual(c_name, ctx.name)
        self.assertTrue(ctx.is_default)

class UpdateTest(AjaxTestBase):

    def test_update_item(self):
        # status cannot be changed
        old = Item(name='howow', description='klakla', # status=Item.WAITING_FOR,
                   parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        data = {"name": 'item25', "description": "test desc", #"status": Item.SOMEDAY,
                "parent": p2.id}

        response = Client().post(reverse('gtdmanager:item_update', kwargs={"item_id": old.id}), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        self.checkModel(Item, data, p2)

    def test_update_project(self):
        old = Project(name='proj', description='ultimate', parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        data = {"name": 'betterProj', "description": "", "parent": p2.id}

        response = Client().post(reverse('gtdmanager:project_update', kwargs={"item_id": old.id}), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.PROJECT
        self.checkModel(Project, data, p2)

    def test_update_next(self):
        old = Next(name='nxt', description='', parent=createParent('par1'))
        old.save()
        p2 = createParent('par2')
        new_ctx = Context(name='neverwhere')
        new_ctx.save()
        data = {"name": 'Do me now', "description": "TODO", "parent": p2.id, "contexts": [new_ctx.id]}

        response = Client().post(reverse('gtdmanager:next_update', kwargs={"item_id": old.id}), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.NEXT
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

        response = Client().post(reverse('gtdmanager:reminder_update', kwargs={"item_id": old.id}), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        data["status"] = Item.REMINDER;
        rem = self.checkModel(Reminder, data, new_parent)
        timeDB = timezone.localtime(rem.remind_at).strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(s, timeDB)
        self.assertItemsEqual([new_ctx], rem.contexts.all())

    def test_update_context(self):
        old = Context.objects.default_context()
        data = {"name": 'newname'}
        response = Client().post(reverse('gtdmanager:context_update', kwargs={"item_id": old.id}), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))

        new = Context.objects.get(name=data['name'])
        self.assertEqual(data['name'], new.name)

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

        response = Client().get(reverse('gtdmanager:context_delete', kwargs={"ctx_id": ctx.id}))
        self.assertEqual(200, response.status_code)
        self.assertEqual({"success": True}, json.loads(response.content))
        self.assertEquals(1, Context.objects.count())
        self.assertEquals(def_ctx, Context.objects.first())

class CompleteTest(DeleteCompleteBaseTest):

    def exec_template(self, cls, name, prefix):
        self.base_template(cls, name, prefix, 'complete', Item.COMPLETED)


class GetFormTest(AjaxTestBase):

    def check_response(self, response):
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        return data['form_html']

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
        item = Item(name=name)
        item.save()

        #url = '/%sgtdmanager.item_get_form/?argv={"item_id":%d}' % (dajaxice_config.dajaxice_url[1:], item.id)
        response = Client().get(reverse('gtdmanager:item_form', kwargs={"item_id": item.id}))
        self.assertEqual(200, response.status_code)

        html = self.check_response(response)
        actionURL = reverse('gtdmanager:item_update', kwargs={"item_id": item.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_project(self):
        name = 'test_name'
        p = Project(name=name)
        p.save()

        response = Client().get(reverse('gtdmanager:project_form', kwargs={"item_id": p.id}))
        self.assertEqual(200, response.status_code)

        html = self.check_response(response)
        actionURL = reverse('gtdmanager:project_update', kwargs={"item_id": p.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_next(self):
        name = 'nxt_NaMe'
        nxt = Next(name=name)
        nxt.save()

        response = Client().get(reverse('gtdmanager:next_form', kwargs={"item_id": nxt.id}))
        self.assertEqual(200, response.status_code)

        html = self.check_response(response)
        actionURL = reverse('gtdmanager:next_update', kwargs={"item_id": nxt.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_reminder(self):
        name = 'rmd'
        r = Reminder(name=name)
        r.save()

        response = Client().get(reverse('gtdmanager:reminder_form', kwargs={"item_id": r.id}))
        self.assertEqual(200, response.status_code)

        html = self.check_response(response)
        actionURL = reverse('gtdmanager:reminder_update', kwargs={"item_id": r.id})
        self.check_base_fields(html, actionURL)
        self.assertIn('value="'+name+'"', html)

    def test_getform_context(self):
        ctx = Context.objects.default_context()
        response = Client().get(reverse('gtdmanager:context_form', kwargs={"ctx_id": ctx.id}))
        self.assertEqual(200, response.status_code)

        html = self.check_response(response)
        actionURL = reverse('gtdmanager:context_update', kwargs={"ctx_id": ctx.id})
        self.check_minimal_fields(html, actionURL)
        self.assertIn('value="'+ctx.name+'"', html)
