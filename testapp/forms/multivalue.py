from django import forms


class PhoneWidget(forms.MultiWidget):

    def decompress(self, value):
        if value is None:
            return ['' * 3]
        return value.split('-')


class PhoneField(forms.MultiValueField):

    widget = PhoneWidget(widgets=[forms.TextInput, forms.TextInput, forms.TextInput])

    def __init__(self, **kwargs):
        super().__init__(fields=(forms.CharField(), forms.CharField(), forms.CharField()), **kwargs)

    def compress(self, data_list):
        return '-'.join(data_list)


class MultiValueForm(forms.Form):
    name = forms.CharField()
    phone_number = PhoneField(label="Phone Number")
