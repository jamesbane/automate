from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div
from django import forms
from django.contrib.auth.models import User
from django_select2 import forms as s2forms

from reseller.models import ResellerPlatform, ResellerCount


class CallCountForm(forms.Form):
    select_all = forms.BooleanField(initial=False, required=False)
    reseller_names = forms.MultipleChoiceField(label='Reseller Names',
                                               widget=s2forms.Select2MultipleWidget,
                                               choices=[],
                                               required=False)
    start_datetime = forms.DateTimeField(label='Start Datetime', required=False,
                                         input_formats=['%Y/%m/%d %H:%M'])
    end_datetime = forms.DateTimeField(label='End Datetime', required=False,
                                       input_formats=['%Y/%m/%d %H:%M'])

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super(CallCountForm, self).__init__(*args, **kwargs)
        if user_id is not None:
            current_user = User.objects.get(pk=user_id)
            self.fields['reseller_names'].choices = ResellerCount.objects.filter(
                customer__in=current_user.groups.all()).values_list('territory_name', 'territory_name').distinct()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Column(
                Div(
                    'select_all', 'reseller_names'
                ),
                Row(
                    Div(
                        AppendedText('start_datetime', '<i class="far fa-calendar"></i>',
                                     css_class='form-control'), css_class='col-4'),
                    Div(
                        AppendedText('end_datetime', '<i class="far fa-calendar"></i>',
                                     css_class='form-control'), css_class='col-4'),
                )
            )
        )


class ResellerPlatformForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ResellerPlatform
        exclude = []
