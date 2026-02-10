"""
Smart Healthcare Billing Platform - Django Backend
Single-file implementation with REST API endpoints
"""

import os
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import path
from django.core.management import execute_from_command_line
import json
from datetime import datetime
from decimal import Decimal

# ============================================================================
# CONFIGURATION
# ============================================================================

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='smart-healthcare-billing-secret-key-2024',
        ALLOWED_HOSTS=['*'],
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'healthcare_billing.db',
            }
        },
        CORS_ALLOW_ALL_ORIGINS=True,
    )
    django.setup()

# ============================================================================
# MODELS
# ============================================================================

class Medicine(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, null=True, blank=True)
    govt_min_price = models.DecimalField(max_digits=10, decimal_places=2)
    govt_max_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'healthcare'
        db_table = 'medicines'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'govt_min_price': float(self.govt_min_price),
            'govt_max_price': float(self.govt_max_price),
            'unit': self.unit,
            'created_at': self.created_at.isoformat()
        }


class Procedure(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, null=True, blank=True)
    govt_min_price = models.DecimalField(max_digits=10, decimal_places=2)
    govt_max_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'healthcare'
        db_table = 'procedures'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'govt_min_price': float(self.govt_min_price),
            'govt_max_price': float(self.govt_max_price),
            'created_at': self.created_at.isoformat()
        }


class Bill(models.Model):
    patient_name = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=255)
    bill_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    verified = models.BooleanField(default=False)
    overcharged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'healthcare'
        db_table = 'bills'
        ordering = ['-created_at']

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'hospital_name': self.hospital_name,
            'bill_date': self.bill_date.isoformat(),
            'total_amount': float(self.total_amount),
            'verified': self.verified,
            'overcharged': self.overcharged,
            'created_at': self.created_at.isoformat()
        }


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=50)  # 'medicine' or 'procedure'
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=255)
    charged_price = models.DecimalField(max_digits=10, decimal_places=2)
    govt_max_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_overcharged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'healthcare'
        db_table = 'bill_items'

    def to_dict(self):
        return {
            'id': self.id,
            'bill_id': self.bill_id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'charged_price': float(self.charged_price),
            'govt_max_price': float(self.govt_max_price),
            'is_overcharged': self.is_overcharged,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# API VIEWS
# ============================================================================

def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False)

def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status)


@csrf_exempt
@require_http_methods(["GET"])
def get_medicines(request):
    """Get all medicines"""
    medicines = Medicine.objects.all()
    return json_response([m.to_dict() for m in medicines])


@csrf_exempt
@require_http_methods(["GET"])
def get_procedures(request):
    """Get all procedures"""
    procedures = Procedure.objects.all()
    return json_response([p.to_dict() for p in procedures])


@csrf_exempt
@require_http_methods(["GET"])
def search_item(request):
    """Search medicine or procedure by name"""
    query = request.GET.get('q', '')
    item_type = request.GET.get('type', 'medicine')
    
    if not query:
        return error_response('Query parameter required')
    
    if item_type == 'medicine':
        items = Medicine.objects.filter(name__icontains=query)[:10]
    else:
        items = Procedure.objects.filter(name__icontains=query)[:10]
    
    return json_response([item.to_dict() for item in items])


@csrf_exempt
@require_http_methods(["POST"])
def check_price(request):
    """Check if price is within government limits"""
    try:
        data = json.loads(request.body)
        item_name = data.get('item_name')
        item_type = data.get('item_type')
        charged_price = Decimal(str(data.get('charged_price')))
        save_to_db = data.get('save_to_db', False)
        
        # Search for item
        if item_type == 'medicine':
            items = Medicine.objects.filter(name__icontains=item_name)
        else:
            items = Procedure.objects.filter(name__icontains=item_name)
        
        if not items.exists():
            return json_response({
                'found': False,
                'message': 'Item not found in government database'
            })
        
        item = items.first()
        is_valid = item.govt_min_price <= charged_price <= item.govt_max_price
        overcharge = max(0, charged_price - item.govt_max_price)
        
        result = {
            'found': True,
            'item': item.to_dict(),
            'charged_price': float(charged_price),
            'is_valid': is_valid,
            'overcharge': float(overcharge),
            'message': 'Price is within government limits' if is_valid else f'Overcharged by ₹{overcharge}'
        }
        
        # Save to database if requested
        if save_to_db:
            Bill.objects.create(
                patient_name='Quick Check',
                hospital_name='Price Verification',
                bill_date=datetime.now().date(),
                total_amount=charged_price,
                verified=True,
                overcharged=not is_valid
            )
        
        return json_response(result)
        
    except Exception as e:
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def verify_bill(request):
    """Verify complete bill with multiple items"""
    try:
        data = json.loads(request.body)
        patient_name = data.get('patient_name')
        hospital_name = data.get('hospital_name')
        bill_date = data.get('bill_date')
        items = data.get('items', [])
        
        if not all([patient_name, hospital_name, bill_date, items]):
            return error_response('Missing required fields')
        
        # Verify each item
        verified_items = []
        total_amount = Decimal('0')
        has_overcharge = False
        
        for item_data in items:
            item_name = item_data['name']
            item_type = item_data['type']
            charged_price = Decimal(str(item_data['price']))
            total_amount += charged_price
            
            # Find item in database
            if item_type == 'medicine':
                db_items = Medicine.objects.filter(name__icontains=item_name)
            else:
                db_items = Procedure.objects.filter(name__icontains=item_name)
            
            if db_items.exists():
                db_item = db_items.first()
                is_valid = db_item.govt_min_price <= charged_price <= db_item.govt_max_price
                
                if not is_valid:
                    has_overcharge = True
                
                verified_items.append({
                    'item_id': db_item.id,
                    'item_name': db_item.name,
                    'item_type': item_type,
                    'charged_price': charged_price,
                    'govt_max_price': db_item.govt_max_price,
                    'is_overcharged': not is_valid
                })
        
        # Create bill
        bill = Bill.objects.create(
            patient_name=patient_name,
            hospital_name=hospital_name,
            bill_date=bill_date,
            total_amount=total_amount,
            verified=True,
            overcharged=has_overcharge
        )
        
        # Create bill items
        for item in verified_items:
            BillItem.objects.create(
                bill=bill,
                item_type=item['item_type'],
                item_id=item['item_id'],
                item_name=item['item_name'],
                charged_price=item['charged_price'],
                govt_max_price=item['govt_max_price'],
                is_overcharged=item['is_overcharged']
            )
        
        return json_response({
            'success': True,
            'bill_id': bill.id,
            'bill': bill.to_dict()
        })
        
    except Exception as e:
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["GET"])
def get_bills(request):
    """Get all verified bills"""
    bills = Bill.objects.all()
    return json_response([bill.to_dict() for bill in bills])


@csrf_exempt
@require_http_methods(["GET"])
def get_bill_details(request, bill_id):
    """Get bill with all items"""
    try:
        bill = Bill.objects.get(id=bill_id)
        items = BillItem.objects.filter(bill=bill)
        
        return json_response({
            'bill': bill.to_dict(),
            'items': [item.to_dict() for item in items]
        })
    except Bill.DoesNotExist:
        return error_response('Bill not found', 404)


@csrf_exempt
@require_http_methods(["GET"])
def dashboard_stats(request):
    """Get dashboard statistics"""
    total_bills = Bill.objects.count()
    overcharged_bills = Bill.objects.filter(overcharged=True).count()
    valid_bills = total_bills - overcharged_bills
    
    return json_response({
        'total_bills': total_bills,
        'overcharged_bills': overcharged_bills,
        'valid_bills': valid_bills
    })


def home(request):
    """API documentation"""
    return JsonResponse({
        'message': 'Smart Healthcare Billing API',
        'version': '1.0',
        'endpoints': {
            'GET /api/medicines/': 'Get all medicines',
            'GET /api/procedures/': 'Get all procedures',
            'GET /api/search/?q=name&type=medicine': 'Search items',
            'POST /api/check-price/': 'Check single price',
            'POST /api/verify-bill/': 'Verify complete bill',
            'GET /api/bills/': 'Get all bills',
            'GET /api/bills/<id>/': 'Get bill details',
            'GET /api/stats/': 'Get dashboard statistics'
        }
    })

# ============================================================================
# URL ROUTING
# ============================================================================

urlpatterns = [
    path('', home),
    path('api/medicines/', get_medicines),
    path('api/procedures/', get_procedures),
    path('api/search/', search_item),
    path('api/check-price/', check_price),
    path('api/verify-bill/', verify_bill),
    path('api/bills/', get_bills),
    path('api/bills/<int:bill_id>/', get_bill_details),
    path('api/stats/', dashboard_stats),
]

application = get_wsgi_application()

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Initialize database with tables and sample data"""
    from django.core.management import call_command
    from django.db import connection
    
    # Create tables
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Medicine)
        schema_editor.create_model(Procedure)
        schema_editor.create_model(Bill)
        schema_editor.create_model(BillItem)
    
    # Add sample data
    if not Medicine.objects.exists():
        medicines = [
            Medicine(name='Paracetamol 500mg', category='Pain Relief', govt_min_price=2.00, govt_max_price=5.00, unit='tablet'),
            Medicine(name='Amoxicillin 250mg', category='Antibiotic', govt_min_price=5.00, govt_max_price=12.00, unit='capsule'),
            Medicine(name='Metformin 500mg', category='Diabetes', govt_min_price=3.00, govt_max_price=8.00, unit='tablet'),
            Medicine(name='Atorvastatin 10mg', category='Cholesterol', govt_min_price=8.00, govt_max_price=20.00, unit='tablet'),
            Medicine(name='Omeprazole 20mg', category='Gastric', govt_min_price=4.00, govt_max_price=10.00, unit='capsule'),
        ]
        Medicine.objects.bulk_create(medicines)
    
    if not Procedure.objects.exists():
        procedures = [
            Procedure(name='Blood Test - Complete', category='Diagnostic', govt_min_price=200.00, govt_max_price=500.00),
            Procedure(name='X-Ray Chest', category='Imaging', govt_min_price=300.00, govt_max_price=800.00),
            Procedure(name='ECG', category='Cardiac', govt_min_price=150.00, govt_max_price=400.00),
            Procedure(name='Ultrasound Abdomen', category='Imaging', govt_min_price=500.00, govt_max_price=1500.00),
            Procedure(name='General Consultation', category='Consultation', govt_min_price=200.00, govt_max_price=600.00),
        ]
        Procedure.objects.bulk_create(procedures)
    
    print("✅ Database initialized with sample data")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            init_database()
        elif sys.argv[1] == 'runserver':
            port = sys.argv[2] if len(sys.argv) > 2 else '8000'
            print(f"🚀 Starting server on http://127.0.0.1:{port}")
            execute_from_command_line(['manage.py', 'runserver', port])
        else:
            execute_from_command_line(sys.argv)
    else:
        print("Usage:")
        print("  python backend.py init          - Initialize database")
        print("  python backend.py runserver     - Start server (default port 8000)")
        print("  python backend.py runserver 8080 - Start server on custom port")
