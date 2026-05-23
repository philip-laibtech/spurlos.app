from django.db import models


class Company(models.Model):
    class CompanyType(models.TextChoices):
        PROSPECT = "prospect", "Prospect"
        CUSTOMER = "customer", "Customer"
        SUPPLIER = "supplier", "Supplier"
        PARTNER = "partner", "Partner"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ARCHIVED = "archived", "Archived"
        DUPLICATE = "duplicate", "Duplicate"

    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    company_type = models.CharField(
        max_length=50,
        choices=CompanyType.choices,
        default=CompanyType.PROSPECT,
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    main_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    hq_location = models.ForeignKey(
        "crm.CompanyLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "companies"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["company_type"]),
        ]

    def __str__(self):
        return self.name


class CompanyLocation(models.Model):
    class LocationType(models.TextChoices):
        HQ = "hq", "HQ"
        OFFICE = "office", "Office"
        BRANCH = "branch", "Branch"
        WAREHOUSE = "warehouse", "Warehouse"
        BILLING = "billing", "Billing"
        OTHER = "other", "Other"

    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.CASCADE,
        related_name="locations",
    )
    address = models.ForeignKey(
        "crm.Address",
        on_delete=models.PROTECT,
        related_name="company_locations",
    )
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=50,
        choices=LocationType.choices,
        default=LocationType.OFFICE,
    )
    is_headquarters = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["type"]),
            models.Index(fields=["is_headquarters"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company"],
                condition=models.Q(is_headquarters=True),
                name="unique_company_hq",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class CompanyPhoneNumber(models.Model):
    class PhoneType(models.TextChoices):
        MAIN = "main", "Main"
        SALES = "sales", "Sales"
        SUPPORT = "support", "Support"
        FINANCE = "finance", "Finance"
        IT = "it", "IT"
        OTHER = "other", "Other"

    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.CASCADE,
        related_name="phone_numbers",
    )
    location = models.ForeignKey(
        "crm.CompanyLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="phone_numbers",
    )
    phone_number = models.CharField(max_length=50)
    label = models.CharField(max_length=100, blank=True)
    type = models.CharField(
        max_length=50,
        choices=PhoneType.choices,
        default=PhoneType.MAIN,
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["location"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company"],
                condition=models.Q(is_primary=True),
                name="unique_company_primary_phone",
            )
        ]

    def __str__(self):
        return self.phone_number
