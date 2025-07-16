from django.shortcuts import render, redirect, get_object_or_404
from .models import Company,Template
from .forms import CompanyForm
from django.http import HttpResponse
import pandas as pd
from django.utils import timezone
from django.template.loader import render_to_string
import tempfile
import pdfkit



def generate_notice(request):
    templates = Template.objects.all()
    companies = Company.objects.all()

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        template_id = request.POST.get('template')
        company_id = request.POST.get('company')

        if not (excel_file and template_id and company_id):
            return HttpResponse("Missing input", status=400)

        template = Template.objects.get(pk=template_id)
        company = Company.objects.get(pk=company_id)

        # Read the Excel file
        df = pd.read_excel(excel_file)

        # Generate all notices
        notices = []
        for _, row in df.iterrows():
            context = {
                'date': timezone.now().strftime('%d-%m-%Y'),
                'name': row['Name'],
                'address': row['Address'],
                'email': row['Email'],
                'loan_id': row['Loan ID'],
                'installments': row['Installments'],
                'overdue_amount': row['Overdue Amount'],
                'month_year': row['Month Year'],
                'costs': row.get('Costs', '0'),
                'company_name': company.name,
                'company_address': company.address,
            }
            # Fill in placeholders in template content
            notice_text = template.content.format(**context)
            notices.append(notice_text)

        #  Render the PDF HTML with all notices
        html_string = render_to_string(
            'notice_pdf.html',
            {
                'notices': notices,
                'notices_count': len(notices),
            }
        )

        #  Write HTML to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
            tmp_file.write(html_string.encode('utf-8'))
            tmp_file_path = tmp_file.name

        #  Generate the PDF from the local HTML file
        pdf = pdfkit.from_file(tmp_file_path, False)

        #  Return the PDF to download
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="legal_notices.pdf"'
        return response

    # If GET: show the form to upload Excel and select options
    return render(request, 'generate_notice.html', {
        'templates': templates,
        'companies': companies,
    })




def home(request):
    return render(request, 'home.html')



def dashboard(request):
    total_companies = Company.objects.count()
    total_templates = Template.objects.count()
    total_notices = 123  # Replace with your real logic
    return render(request, 'dashboard.html', {
        'total_companies': total_companies,
        'total_templates': total_templates,
        'total_notices': total_notices,
    })




#template management functions

def manage_templates(request):
    templates = Template.objects.all()
    print("Templates in DB:", templates)
    return render(request, 'manage_templates.html', {'templates': templates})


def template_detail(request, id):
    template = Template.objects.get(id=id)
    return render(request, 'template_detail.html', {'template': template})



#company management functions

def manage_companies(request):
    companies = Company.objects.all()
    print("Companies in DB:", companies)
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
