from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import CustomUser, Member, Profile, Withdrawal

# Get the custom user model
User = get_user_model()

# Unregister if already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'phone', 'is_staff', 'is_active')
    search_fields = ('name', 'phone')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# Member Admin
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'referral', 'domain', 'payment_id', 'payment_status')
    search_fields = ('user__phone', 'referral', 'payment_id')
    list_filter = ('payment_status',)  # Adding a filter for payment status

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.exclude(is_staff=True)  # Exclude admin users
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'withdrawal_amount', 'phone_number']
    list_editable = ['balance', 'withdrawal_amount', 'phone_number']
    search_fields = ('user__phone',)
    list_filter = ('balance',)  # Adding filter for balance

# Withdrawal Admin
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'ifsc_code', 'amount', 'payment_status', 'created_at')
    search_fields = ('name', 'account_number', 'ifsc_code')
    list_filter = ('payment_status',)  # Adding filter for payment status
    ordering = ('-created_at',)  # Ordering by creation date, descending

    # Optionally, you can make some fields readonly or editable
    readonly_fields = ('created_at',)  # Make 'created_at' field readonly
    # If you want to add more fields for better customization, you can do it like:
    # fields = ('name', 'account_number', 'amount', 'payment_status', 'created_at')

