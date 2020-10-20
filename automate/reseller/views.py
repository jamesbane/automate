from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.views import View
from django.views.generic import FormView

from reseller.forms import CallCountForm
from reseller.models import ResellerCount
from reseller.tasks import reseller_count


class CallCountFormView(LoginRequiredMixin, FormView):
    template_name = 'reseller/call_count_form.html'
    form_class = CallCountForm

    def form_valid(self, form):
        return super(self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = CallCountForm(request.POST)
        select_all = False
        reseller_names = ''
        start_datetime = None
        end_datetime = None
        if form.is_valid():
            select_all = form.cleaned_data['select_all']
            reseller_names = form.cleaned_data['reseller_names']
            start_datetime = form.cleaned_data['start_datetime']
            end_datetime = form.cleaned_data['end_datetime']
        else:
            print(form.errors)

        q = Q()
        if reseller_names != '' and not select_all:
            name_array = [name.strip() for name in reseller_names.split(',')]
            q.add(Q(territory_name__in=name_array), Q.AND)
        if start_datetime is not None:
            q.add(Q(created_at__gt=start_datetime), Q.AND)
        if end_datetime is not None:
            q.add(Q(created_at__lt=end_datetime), Q.AND)

        items = ResellerCount.objects.filter(q).all()
        datas = {}
        for item in items:
            if item.territory_id not in datas:
                datas[item.territory_id] = []
            datas[item.territory_id].append({
                'name': item.territory_name,
                'count': item.count_external,
                'created_at': item.created_at.strftime("%Y-%m-%d %H:%M")
            })
        return JsonResponse({
            'datas': datas
        })

    def get(self, request, *args, **kwargs):
        # reseller_count.apply_async(kwargs={
        #     'user_id': self.request.user.id
        # })
        return super().get(request, *args, **kwargs)
