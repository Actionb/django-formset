import pytest
from django import forms
from django.urls import path

from formset.views import FormView


class MultiWidget(forms.MultiWidget):

    def decompress(self, value):
        if value is None:
            return ['' * 3]
        return value.split('-')


class MultiValueField(forms.MultiValueField):
    widget = MultiWidget(widgets=[forms.TextInput, forms.TextInput, forms.TextInput])

    def __init__(self, **kwargs):
        super().__init__(fields=(forms.CharField(), forms.CharField(), forms.CharField()), **kwargs)

    def compress(self, data_list):
        return '-'.join(data_list)


class TestForm(forms.Form):
    multi_value_field = MultiValueField()


class ControlForm(forms.Form):
    normal_field = forms.CharField()


class NativeFormView(FormView):
    template_name = 'testapp/native-form.html'


urlpatterns = [
    path('test_multi_value_field', NativeFormView.as_view(form_class=TestForm), name='multi-value'),
    path('control', NativeFormView.as_view(form_class=ControlForm), name='control'),
]


@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['multi-value', 'control'])
def test_field_group_fully_initialized(page, viewname):
    """
    Assert that the form's field group is fully initialized.

    If the FieldGroup constructor completed successfully, the group should have
    the css class `dj-untouched`.
    """
    field_group = page.query_selector('django-formset django-field-group')
    assert 'dj-untouched' in field_group.get_attribute('class')
