import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.generic import FormView

from reseller.forms import CallCountForm
from reseller.models import ResellerCount


class CallCountFormView(LoginRequiredMixin, FormView):
    template_name = 'reseller/call_count_form.html'
    form_class = CallCountForm

    def get_form_kwargs(self):
        kwargs = super(CallCountFormView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.id
        return kwargs

    def form_valid(self, form):
        return super(CallCountFormView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = CallCountForm(request.POST, user_id=request.user.id)
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
        q.add(Q(customer__in=request.user.groups.all()), Q.AND)
        if len(reseller_names) > 0 and not select_all:
            name_array = [name.strip() for name in reseller_names]
            q.add(Q(territory_name__in=name_array), Q.AND)
        if start_datetime is not None:
            q.add(Q(created_at__gt=start_datetime), Q.AND)
        if end_datetime is not None:
            q.add(Q(created_at__lt=end_datetime), Q.AND)

        items = ResellerCount.objects.filter(q).all()
        count_data = {}
        datas = {}
        for item in items:
            if item.territory_id not in datas:
                datas[item.territory_id] = []
            datas[item.territory_id].append({
                'name': item.territory_name,
                'count': item.count_external,
                'created_at': item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            if item.created_at.strftime("%Y-%m-%d %H:%M:%S") not in count_data:
                count_data[item.created_at.strftime("%Y-%m-%d %H:%M:%S")] = []
            count_data[item.created_at.strftime("%Y-%m-%d %H:%M:%S")].append({
                'id': item.territory_id,
                'name': item.territory_name,
                'count': item.count_external,
                'created_at': item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return JsonResponse({
            'status': 'success' if len(items) > 0 else 'error',
            'datas': datas,
            'count_data': count_data
        })


class ExportCSVFormView(LoginRequiredMixin, FormView):
    form_class = CallCountForm

    def post(self, request, *args, **kwargs):
        form = CallCountForm(request.POST, user_id=request.user.id)
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
        q.add(Q(customer__in=request.user.groups.all()), Q.AND)
        if len(reseller_names) > 0 and not select_all:
            name_array = [name.strip() for name in reseller_names]
            q.add(Q(territory_name__in=name_array), Q.AND)
        if start_datetime is not None:
            q.add(Q(created_at__gt=start_datetime), Q.AND)
        if end_datetime is not None:
            q.add(Q(created_at__lt=end_datetime), Q.AND)

        items = ResellerCount.objects.filter(q).all()
        datas = {}
        for item in items:
            if item.created_at.strftime("%Y-%m-%d %H:%M:%S") not in datas:
                datas[item.created_at.strftime("%Y-%m-%d %H:%M:%S")] = []
            datas[item.created_at.strftime("%Y-%m-%d %H:%M:%S")].append({
                'id': item.territory_id,
                'name': item.territory_name,
                'count': item.count_external,
                'created_at': item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="export.csv"'

        writer = csv.writer(response)
        csv_header = ['No', 'Sum', 'Date/Time']
        for item in datas[list(datas.keys())[0]]:
            csv_header.append(item['name'])
        writer.writerow(csv_header)
        index = 1
        for key in datas:
            data = datas[key]
            csvdata = [index, 0, '']
            sum_row = 0
            for item in data:
                sum_row += item['count']
                csvdata.append(item['count'])
            csvdata[1] = sum_row
            csvdata[2] = key
            writer.writerow(csvdata)
            index += 1
        return response
