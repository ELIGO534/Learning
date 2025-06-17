from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import CustomUser, Member, Profile, Withdrawal, SponsorshipSurvey, UserActivity

# Get the custom user model
User = get_user_model()

# Unregister if already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'phone', 'is_staff', 'is_active', 'date_joined', 'last_login')
    search_fields = ('name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('date_joined', 'last_login')}),
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
    list_display = ('user', 'referral', 'domain', 'payment_id', 'payment_status', 'created_at')
    search_fields = ('user__phone', 'referral', 'payment_id')
    list_filter = ('payment_status', 'domain', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.exclude(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'withdrawal_amount', 'phone_number', 'earnings', 'login_count', 'last_activity')
    list_editable = ('balance', 'withdrawal_amount')
    search_fields = ('user__phone', 'phone_number')
    list_filter = ('has_collected_stage1',)
    readonly_fields = ('last_activity',)
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Balance Info', {'fields': ('balance', 'withdrawal_amount', 'earnings')}),
        ('Profile Info', {'fields': ('profile_picture', 'phone_number')}),
        ('Activity Tracking', {'fields': ('login_count', 'last_activity', 'has_collected_stage1')}),
    )

# Withdrawal Admin
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'amount', 'payment_method', 'payment_status', 'created_at', 'processed_at')
    search_fields = ('user__phone', 'name', 'account_number', 'ifsc_code')
    list_filter = ('payment_status', 'payment_method', 'created_at')
    readonly_fields = ('created_at', 'processed_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_paid', 'mark_as_rejected']

    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Withdrawal Details', {'fields': ('name', 'account_number', 'ifsc_code', 'amount', 'payment_method')}),
        ('Status', {'fields': ('payment_status', 'processed_at')}),
    )

    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(payment_status='Pending').update(
            payment_status='Paid',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawals marked as paid.')

    def mark_as_rejected(self, request, queryset):
        for withdrawal in queryset.filter(payment_status='Pending'):
            withdrawal.payment_status = 'Rejected'
            withdrawal.save()
        self.message_user(request, f'{queryset.count()} withdrawals marked as rejected.')

    mark_as_paid.short_description = "Mark selected withdrawals as Paid"
    mark_as_rejected.short_description = "Mark selected withdrawals as Rejected"

# Sponsorship Survey Admin
@admin.register(SponsorshipSurvey)
class SponsorshipSurveyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'college', 'year', 'contact', 'source', 'internship', 'updates', 'is_contacted')
    list_filter = ('year', 'source', 'internship', 'updates', 'is_contacted')
    search_fields = ('full_name', 'email', 'college', 'contact')
    readonly_fields = ('created_at', 'formatted_interest')
    date_hierarchy = 'created_at'
    actions = ['mark_as_contacted']

    fieldsets = (
        ('Personal Info', {'fields': ('full_name', 'email', 'contact')}),
        ('Education', {'fields': ('college', 'year')}),
        ('Survey Info', {'fields': ('source', 'formatted_interest', 'internship', 'updates')}),
        ('Admin', {'fields': ('is_contacted', 'notes', 'created_at')}),
    )

    def formatted_interest(self, obj):
        return ", ".join(obj.interest.split(',')) if obj.interest else "-"
    formatted_interest.short_description = "Interests"

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(is_contacted=True)
        self.message_user(request, f'{updated} surveys marked as contacted.')
    mark_as_contacted.short_description = "Mark selected as contacted"

# User Activity Admin
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'truncated_details', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__phone', 'action', 'ip_address')
    readonly_fields = ('user', 'action', 'details', 'timestamp', 'ip_address', 'user_agent')
    date_hierarchy = 'timestamp'

    def truncated_details(self, obj):
        return str(obj.details)[:50] + '...' if len(str(obj.details)) > 50 else str(obj.details)
    truncated_details.short_description = 'Details'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False