import csv
from datetime import datetime
from decimal import Decimal

SUPPORTED_SOURCE_TYPES = ['sap-fuel', 'utility-electricity', 'travel-corporate']

SAP_FUEL_FIELDS = {
    'posting_date': ['Posting Date', 'Buchungsdatum', 'Date'],
    'quantity': ['Quantity', 'Menge', 'Qty'],
    'unit': ['UoM', 'Unit'],
    'vendor': ['Vendor', 'Supplier'],
    'plant': ['Plant Code', 'Werks'],
    'item_description': ['Material Description', 'Description'],
    'emissions': ['CO2 Emissions', 'Emissions', 'CO2'],
}

UTILITY_FIELDS = {
    'billing_start': ['Billing Start', 'Period Start', 'Start Date'],
    'billing_end': ['Billing End', 'Period End', 'End Date'],
    'usage': ['Usage (kWh)', 'Usage', 'kWh'],
    'meter': ['Meter ID', 'Meter'],
    'account': ['Account Number', 'Account'],
    'cost': ['Cost', 'Amount'],
}

TRAVEL_FIELDS = {
    'expense_type': ['Expense Type', 'Category'],
    'trip_start': ['Trip Start', 'Start Date'],
    'trip_end': ['Trip End', 'End Date'],
    'origin': ['Origin', 'From'],
    'destination': ['Destination', 'To'],
    'distance': ['Distance', 'Miles', 'Km'],
    'amount': ['Amount', 'Cost'],
    'currency': ['Currency'],
}

EMISSION_FACTORS = {
    'diesel': 2.68,
    'petrol': 2.31,
    'electricity': 0.42,
    'flight': 0.18,
    'ground': 0.13,
    'hotel': 0.025,
}


def find_column(row, choices):
    for key in row:
        normalized = key.strip()
        for variant in choices:
            if normalized.lower() == variant.lower():
                return key
    return None


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y/%m/%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def parse_decimal(value):
    if value is None:
        return None
    try:
        return float(Decimal(value.strip().replace(',', '.')))
    except Exception:
        return None


def read_csv_rows(file_obj):
    sample = file_obj.read(2048)
    file_obj.seek(0)
    if not sample:
        return []
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;')
    except csv.Error:
        dialect = csv.get_dialect('excel')
    file_obj.seek(0)
    reader = csv.DictReader(file_obj, dialect=dialect)
    return [row for row in reader if any(value.strip() for value in row.values() if value)]


def normalize_sap_row(row):
    posting_date = parse_date(row.get(find_column(row, SAP_FUEL_FIELDS['posting_date'])))
    quantity = parse_decimal(row.get(find_column(row, SAP_FUEL_FIELDS['quantity'])))
    unit = row.get(find_column(row, SAP_FUEL_FIELDS['unit']), '').strip()
    vendor = row.get(find_column(row, SAP_FUEL_FIELDS['vendor']), '').strip() or 'SAP supplier'
    plant = row.get(find_column(row, SAP_FUEL_FIELDS['plant']), '').strip()
    item_description = row.get(find_column(row, SAP_FUEL_FIELDS['item_description']), '').strip()
    emissions = parse_decimal(row.get(find_column(row, SAP_FUEL_FIELDS['emissions'])))

    normalized_qty = quantity or 0.0
    normalized_unit = unit or 'L'

    if emissions is None and quantity is not None:
        factor = EMISSION_FACTORS['diesel'] if 'diesel' in item_description.lower() or 'diesel' in unit.lower() else EMISSION_FACTORS['petrol']
        emissions = normalized_qty * factor

    suspicious = None
    if not posting_date or not quantity or not unit:
        suspicious = 'missing SAP purchase date, quantity, or unit'

    return {
        'record_type': 'fuel',
        'category': item_description or 'Fuel purchase',
        'emission_scope': 'scope1',
        'activity_start': posting_date,
        'activity_end': posting_date,
        'vendor': vendor,
        'location': plant,
        'quantity': normalized_qty,
        'quantity_unit': normalized_unit,
        'normalized_quantity': normalized_qty,
        'normalized_unit': normalized_unit,
        'emissions_kg_co2e': emissions or 0.0,
        'suspicious_reason': suspicious,
        'raw_payload': row,
    }


def normalize_utility_row(row):
    billing_start = parse_date(row.get(find_column(row, UTILITY_FIELDS['billing_start'])))
    billing_end = parse_date(row.get(find_column(row, UTILITY_FIELDS['billing_end'])))
    usage = parse_decimal(row.get(find_column(row, UTILITY_FIELDS['usage'])))
    meter = row.get(find_column(row, UTILITY_FIELDS['meter']), '').strip()
    account = row.get(find_column(row, UTILITY_FIELDS['account']), '').strip()
    cost = parse_decimal(row.get(find_column(row, UTILITY_FIELDS['cost'])))

    suspicious = None
    if not billing_start or not billing_end or not usage:
        suspicious = 'utility bill missing dates or usage quantity'

    return {
        'record_type': 'electricity',
        'category': 'Electricity',
        'emission_scope': 'scope2',
        'activity_start': billing_start,
        'activity_end': billing_end,
        'vendor': account or 'Utility provider',
        'location': meter,
        'quantity': usage or 0.0,
        'quantity_unit': 'kWh',
        'normalized_quantity': usage or 0.0,
        'normalized_unit': 'kWh',
        'emissions_kg_co2e': (usage or 0.0) * EMISSION_FACTORS['electricity'],
        'suspicious_reason': suspicious,
        'raw_payload': row,
    }


def normalize_travel_row(row):
    expense_type = row.get(find_column(row, TRAVEL_FIELDS['expense_type']), '').strip().lower()
    trip_start = parse_date(row.get(find_column(row, TRAVEL_FIELDS['trip_start'])))
    trip_end = parse_date(row.get(find_column(row, TRAVEL_FIELDS['trip_end'])))
    origin = row.get(find_column(row, TRAVEL_FIELDS['origin']), '').strip()
    destination = row.get(find_column(row, TRAVEL_FIELDS['destination']), '').strip()
    distance = parse_decimal(row.get(find_column(row, TRAVEL_FIELDS['distance'])))
    amount = parse_decimal(row.get(find_column(row, TRAVEL_FIELDS['amount'])))
    currency = row.get(find_column(row, TRAVEL_FIELDS['currency']), '').strip() or 'USD'

    if not distance and origin and destination:
        distance = 500.0 if origin and destination and origin != destination else 0.0

    category = 'Business travel'
    if 'flight' in expense_type:
        record_type = 'flight'
        scope = 'scope3'
        factor = EMISSION_FACTORS['flight']
    elif 'hotel' in expense_type or 'lodging' in expense_type:
        record_type = 'hotel'
        scope = 'scope3'
        factor = EMISSION_FACTORS['hotel']
    else:
        record_type = 'ground'
        scope = 'scope3'
        factor = EMISSION_FACTORS['ground']

    emissions = (distance or 0.0) * factor
    suspicious = None
    if not trip_start or not trip_end or (record_type in ['flight', 'ground'] and not distance):
        suspicious = 'travel record missing dates or distance'

    return {
        'record_type': record_type,
        'category': category,
        'emission_scope': scope,
        'activity_start': trip_start,
        'activity_end': trip_end,
        'vendor': expense_type.title() or 'Travel platform',
        'location': f'{origin} → {destination}',
        'quantity': distance or 0.0,
        'quantity_unit': 'km',
        'normalized_quantity': distance or 0.0,
        'normalized_unit': 'km',
        'emissions_kg_co2e': emissions,
        'suspicious_reason': suspicious,
        'raw_payload': row,
    }


def normalize_row_for_source(source_type, row):
    if source_type == 'sap-fuel':
        return normalize_sap_row(row)
    if source_type == 'utility-electricity':
        return normalize_utility_row(row)
    if source_type == 'travel-corporate':
        return normalize_travel_row(row)
    return None
