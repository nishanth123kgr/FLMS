import reportlab
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the Arial font
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

# Create a new canvas object
c = canvas.Canvas('payslip.pdf')

# Add the university logo to the payslip
c.drawImage('img/logo.png', 20, 700)

# Add the university name and address to the payslip
c.setFont('Arial', 16)
c.drawString(20, 650, 'ANNA UNIVERSITY')
c.drawString(20, 630, 'UNIVERSITY COLLEGE OF ENGINEERING RAMANATHAPURAM')
c.drawString(20, 610, '(A Constituent College of Anna University Chennai)')
c.drawString(20, 590, 'PULLANGUDI, RAMANATHAPURAM-623 513')
c.drawString(20, 570, 'PROGRESS THROUGH KNOWLEDGE')

# Add the payslip title to the payslip
c.setFont('Arial', 18)
c.drawString(300, 650, 'Pay Slip for the Month of JUNE 2023')

# Add the employee information to the payslip
c.setFont('Arial', 16)
c.drawString(20, 500, 'Name: Dr. V.Mugesh Raja')
c.drawString(20, 480, 'Date of Joining: 16.12.2010')
c.drawString(20, 460, 'Employee No.: 943010')
c.drawString(20, 440, 'Scale of Pay: 57700182400')
c.drawString(20, 420, 'Designation: Asst. Professor')
c.drawString(20, 400, 'Name of Bank: Indian Overseas Bank')
c.drawString(20, 380, 'Bank A/c Number: 110201000035663')

# Add the earnings table to the payslip
c.setFont('Arial', 14)
c.drawString(20, 300, 'Earnings (in Rs.)')
c.drawString(20, 280, 'Basic Pay: 87200')
c.drawString(20, 260, 'Dearness Allowance: 36624')
c.drawString(20, 240, 'House Rent Allowance: 3200')
c.drawString(20, 220, 'Medical Allowance: 300')
c.drawString(20, 200, 'Total Earnings: 127324')

# Add the deductions table to the payslip
c.setFont('Arial', 14)
c.drawString(20, 100, 'Deductions (in Rs.)')
c.drawString(20, 80, 'Contributory Pension Scheme: 12382')
c.drawString(20, 60, 'H Insurance Scheme: 300')
c.drawString(20, 40, 'Festival Advance: 0')
c.drawString(20, 20, 'SF Scheme: 110')
c.drawString(20, 0, 'SPF: 70')
c.drawString(300, 200, 'Total Deductions: 27862')

# Add the net payable amount to the payslip
c.setFont('Arial', 16)
c.drawString(300, 100, 'Net Payable: Rs.99462/- (Rupees Ninety Nine Thousand Four Hundred Sixty Two Only)')

# Save the payslip PDF file
c.save()
