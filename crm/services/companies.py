from crm.models import Address, Company, CompanyLocation, CompanyPhoneNumber


def create_company(name: str, **data) -> Company:
    company = Company(name=name, **data)
    company.full_clean()
    company.save()
    return company


def update_company(company: Company, **data) -> Company:
    for field, value in data.items():
        setattr(company, field, value)
    company.full_clean()
    company.save()
    return company


def create_company_location(company: Company, address: Address, name: str, **data) -> CompanyLocation:
    location = CompanyLocation(company=company, address=address, name=name, **data)
    location.full_clean()
    location.save()
    return location



def add_company_phone_number(company: Company, phone_number: str, **data) -> CompanyPhoneNumber:
    phone = CompanyPhoneNumber(company=company, phone_number=phone_number, **data)
    phone.full_clean()
    phone.save()
    return phone
