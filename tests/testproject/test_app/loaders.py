from django.template.loader import BaseLoader

class FakeTemplate(object):

    def render(self, ctx):
        return ctx

class FakeTemplateLoader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        return template_name, template_name

    def get_template_from_string(self, source, origin=None, name=None):
        return FakeTemplate()