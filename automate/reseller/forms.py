from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div
from django import forms


class CallCountForm(forms.Form):
    select_all = forms.BooleanField(initial=False, required=False)
    reseller_names = forms.CharField(label='Reseller Names',
                                     widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
                                     required=False)
    start_datetime = forms.DateTimeField(label='Start Datetime', required=False,
                                         input_formats=['%Y/%m/%d %H:%M'])
    end_datetime = forms.DateTimeField(label='End Datetime', required=False,
                                       input_formats=['%Y/%m/%d %H:%M'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
