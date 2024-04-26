from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin



class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, fullName, password, **other_fields):
        # other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        return self.create_user(email, fullName, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    userTypes = ((1, "customer"), (2, "provider"))
    deviceType = ((1, "Android"), (2, "IOS"))
    genderType = ((1, "He/Him"), (2, "She/Her"), (3, "They/Them"))
    userApprovalStatus = ((1, "pending"), (2, "approved"), (3, "disapproved"))

    firstName = models.CharField(max_length=255, null=False)
    lastName = models.CharField(max_length=255, null=False)
    fullName = models.CharField(max_length=255, null=True)
    mobileNo = models.CharField(max_length=255, unique=True, null=False)
    email = models.EmailField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    dateOfBirth = models.CharField(max_length=255, null=True, default=None)
    zipCode = models.CharField(max_length=255, null=False)
    isActive = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False)
    isVerified = models.BooleanField(default=False)
    countryCode = models.CharField(max_length=255, null=True)
    deviceType = models.IntegerField(choices=deviceType, null=True)
    userType = models.IntegerField(choices=userTypes, null=False, default=None)
    genderType = models.IntegerField(choices=genderType, null=True)
    deviceToken = models.CharField(max_length=255, null=True)
    profileImage = models.CharField(max_length=255, null=True, blank=True)
    lat = models.FloatField(default=0.00, blank=True, null=True)
    lng = models.FloatField(default=0.00, blank=True, null=True)
    state = models.CharField(max_length=255, null=False, default=None)
    last_login = models.DateTimeField(default=now, editable=False)
    isAvailable = models.BooleanField(default=False)
    isApproved = models.IntegerField(
        choices=userApprovalStatus, null=False, default=1)
    admin_forget_password_token = models.CharField(
        max_length=200, default=False, null=True)
    stripeCustomerId = models.CharField(
        max_length=255, null=True, default=None)
    stripeProviderAccountId = models.CharField(
        max_length=255, null=True, default=None)
    isAccountConfigComplete = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName', 'mobileNo']
    objects = CustomAccountManager()


    class Meta:
        db_table = 'users'


class licenseType(models.Model):
    licenseTypeName = models.CharField(max_length=255, null=False)
    therapyType = models.CharField(max_length=255, null=False, default=None)
    category = models.CharField(max_length=255, null=False, default=None)
    description = models.CharField(max_length=255, null=False, default=None)
    requirment = models.CharField(max_length=500, null=False, default=None)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)


    class Meta:
        db_table = 'license_types'


class ProviderUserAdditionalData(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='providerData', db_column='userId')
    experience = models.IntegerField(null=False, default=0)
    about = models.TextField(null=True, default=None)
    fee = models.IntegerField(null=True)
    createdAt = models.DateTimeField(default=now, editable=False)
    
    class Meta:
        db_table = 'provider_user_additional_data'


class PatientUserAdditionalData(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='patientData', db_column='userId')
    minPrice = models.IntegerField(null=True)
    maxPrice = models.IntegerField(null=True)
    shareMedicalRecord = models.IntegerField(null=True, default=0)
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'patient_user_additional_data'


class ProviderUserLicenseDocs(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='providerLicenseDoc', db_column='userId')
    providerUserDocUrl = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'provider_user_docs'


class ProviderStripeAccount(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE, unique=True,
                                  related_name='provider_stipe_ref', db_column='userId')
    stipeAccountId = models.CharField(max_length=255, null=False)
    isCompleted = models.BooleanField(default=False)
    refreshUrl = models.CharField(max_length=255, null=True, blank=True)
    returnUrl = models.CharField(max_length=255, null=True, blank=True)
    loginLink =  models.CharField(max_length=255, null=True, default=None, blank=True)
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'provider_stripe_accounts'
