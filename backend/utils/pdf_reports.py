from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_application_pdf(application):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    margin = 50
    y = height - margin

    def draw_text(text, font_size=12, offset=15, bold=False):
        nonlocal y
        if bold:
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica", font_size)
        c.drawString(margin, y, text)
        y -= offset

    # Title
    draw_text(f"Application Report - {application.property.name}", font_size=16, offset=30, bold=True)

    # Applicant Info
    draw_text("Applicant Information:", font_size=14, offset=20, bold=True)
    draw_text(f"Name: {application.user.name}")
    draw_text(f"Email: {application.user.email}")
    draw_text(f"Phone: {application.user.phone_number}")
    draw_text(f"Marital Status: {application.marital_status}")
    draw_text(f"Employment Status: {application.employment_status}")
    if application.monthly_income:
        draw_text(f"Monthly Income: ${application.monthly_income}")
    draw_text(f"Has Children?: {'Yes' if application.has_children else 'No'}")
    if application.has_children:
        draw_text(f"Number of Children: {application.number_of_children}")
    draw_text(f"Has Pet?: {'Yes' if application.has_pet else 'No'}")
    if application.has_pet:
        draw_text(f"Pet Details: {application.pet_details}")
    draw_text(f"Has Disability?: {'Yes' if application.has_disability else 'No'}")
    if application.has_disability:
        draw_text(f"Disability Details: {application.disability_details}")
    if application.references:
        draw_text("References:", offset=10, bold=True)
        for line in application.references.splitlines():
            draw_text(f"  {line}", offset=12)
    if application.message:
        draw_text("Additional Message:", offset=10, bold=True)
        for line in application.message.splitlines():
            draw_text(f"  {line}", offset=12)

    y -= 10
    draw_text("Property Details:", font_size=14, offset=20, bold=True)
    draw_text(f"Property Name: {application.property.name}")
    draw_text(f"Address: {application.property.address}")
    draw_text(f"Status: {application.status}")
    draw_text(f"Preferred Move-In Date: {application.preferred_move_in_date}")
    draw_text(f"Rental Period: {application.rental_period_months} month(s)")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_contract_pdf(contract):
    from reportlab.lib.pagesizes import letter
    from io import BytesIO
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    margin = 50
    y = height - margin

    def draw_text(text, font_size=12, offset=15, bold=False):
        nonlocal y
        if bold:
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica", font_size)
        c.drawString(margin, y, text)
        y -= offset

    # Title
    draw_text(f"Contract Report - #{contract.contract_number}", font_size=16, offset=30, bold=True)

    # Contract Details
    draw_text("Contract Details:", font_size=14, offset=20, bold=True)
    draw_text(f"Tenant: {contract.tenant.name}")
    draw_text(f"Agent: {contract.agent.name}")
    draw_text(f"Property: {contract.property.name}")
    draw_text(f"Start Date: {contract.start_date}")
    draw_text(f"End Date: {contract.end_date}")
    draw_text(f"Rent Amount: ${contract.rent_amount}")
    draw_text(f"Status: {contract.status}")

    if contract.additional_terms:
        draw_text("Additional Terms:", offset=20, bold=True)
        for line in contract.additional_terms.splitlines():
            draw_text(f"  {line}", offset=12)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
