from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Company, Template
from .forms import CompanyForm
from django.http import HttpResponse
import pandas as pd
from django.utils import timezone
from django.template.loader import render_to_string
import tempfile
import pdfkit


def generate_notice(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            return HttpResponse("Missing input: Please upload an Excel file.", status=400)

        df = pd.read_excel(excel_file)

        notices = []

        for index, row in df.iterrows():
            company_name = row['Company'].strip()
            template_type = row['Template Type'].strip()

            try:
                company = Company.objects.get(name__iexact=company_name)
                template = Template.objects.get(company=company, template_type__iexact=template_type)
            except Company.DoesNotExist:
                return HttpResponse(f"Company '{company_name}' not found.", status=400)
            except Template.DoesNotExist:
                return HttpResponse(f"Template '{template_type}' not found for '{company_name}'.", status=400)

            # Exact context keys
            context = {
                'customer_name': row['Name'],
                'customer_address': row['Address'],
                'email': row['Email'],
                'loan_account': row['Loan Account'],
                'installments': row['Installments'],
                'overdue_amount': row['Overdue Amount'],
                'month_year': row['Month Year'],
                'costs': row['Costs'],
                'advocate_name': row['Advocate Name'],
                'loan_date': row['Loan Date'],
                'installment_amount': row['Installment Amount'],
                'loan_amount': row['Loan Amount'],
                'start_date': row['Start Date'],
                'due_dates': row['Default Dates'],
                'default_dates': row['Default Dates'],
                'company_name': company.name,
                'company_address': company.address,
                'today_date': timezone.now().strftime('%d-%m-%Y'),
                'due_date': timezone.now().strftime('%d-%m-%Y'),
            }

            print("====== DEBUG ROW ======")
            print(f"Row {index+1}: Company={company_name} | Template={template_type}")
            print("Context:", context)

            # Format safely
            try:
                notice_text = template.body.format(**context)
                email_body = template.email_body.format(**context)
            except KeyError as e:
                return HttpResponse(f"Template has undefined placeholder: {str(e)}", status=500)

            notices.append({
                'company_name': company.name,
                'company_address': company.address,
                'subject': template.subject.format(**context),
                'body': notice_text
            })

            # Send email
            email = EmailMessage(
                subject=template.subject.format(**context),
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[row['Email']],
            )
            email.send()
            print(f"✅ Email sent to: {row['Email']}")

        # Generate PDF
        html_string = render_to_string('notice_pdf.html', {
            'notices': notices,
        })

        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
            tmp_file.write(html_string.encode('utf-8'))
            tmp_file_path = tmp_file.name

        pdf = pdfkit.from_file(tmp_file_path, False)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="legal_notices.pdf"'
        return response

    return render(request, 'generate_notice.html')


def home(request):
    return render(request, 'home.html')


def dashboard(request):
    total_companies = Company.objects.count()
    total_templates = Template.objects.count()
    total_notices = 123  # Replace with real logic if needed
    return render(request, 'dashboard.html', {
        'total_companies': total_companies,
        'total_templates': total_templates,
        'total_notices': total_notices,
    })


def manage_templates(request):
    templates = Template.objects.all()
    return render(request, 'manage_templates.html', {'templates': templates})


def template_detail(request, id):
    template = Template.objects.get(id=id)
    return render(request, 'template_detail.html', {'template': template})


def manage_companies(request):
    companies = Company.objects.all()
    return render(request, 'manage_companies.html', {'companies': companies})


def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_companies')
    else:
        form = CompanyForm()
    return render(request, 'add_company.html', {'form': form})


def edit_company(request, id):
    company = get_object_or_404(Company, pk=id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('manage_companies')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'edit_company.html', {'form': form, 'company': company})


def delete_company(request, id):
    company = get_object_or_404(Company, pk=id)
    if request.method == 'POST':
        company.delete()
        return redirect('manage_companies')
    return render(request, 'delete_company.html', {'company': company})
