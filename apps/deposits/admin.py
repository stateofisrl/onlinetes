"""
Deposits admin configuration.
"""

from django.contrib import admin
from django.utils import timezone
from .models import Deposit, CryptoWallet


@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ['cryptocurrency', 'wallet_address', 'is_active', 'created_at']
    list_filter = ['is_active', 'cryptocurrency']
    search_fields = ['cryptocurrency', 'wallet_address']
    ordering = ['cryptocurrency']


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'cryptocurrency', 'amount', 'status', 'created_at']
    list_filter = ['status', 'cryptocurrency', 'created_at']
    search_fields = ['user__email', 'cryptocurrency']
    readonly_fields = []
    actions = ['approve_deposit', 'reject_deposit']
    ordering = ['-created_at']
    
    def get_fieldsets(self, request, obj=None):
        """Return different fieldsets for add vs edit."""
        if obj:  # Editing existing deposit
            return (
                ('User & Deposit Info', {
                    'fields': ('user', 'cryptocurrency', 'amount', 'created_at')
                }),
                ('Proof Details', {
                    'fields': ('proof_type', 'proof_content', 'proof_image')
                }),
                ('Status & Admin Actions', {
                    'fields': ('status', 'admin_notes', 'approved_by', 'approved_at')
                }),
            )
        else:  # Adding new deposit
            return (
                ('User & Deposit Info', {
                    'fields': ('user', 'cryptocurrency', 'amount')
                }),
                ('Proof Details', {
                    'fields': ('proof_type', 'proof_content', 'proof_image')
                }),
                ('Status & Admin Actions', {
                    'fields': ('status', 'admin_notes', 'approved_by', 'approved_at')
                }),
            )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly only when editing existing deposit."""
        if obj:  # Editing existing deposit
            return ['user', 'cryptocurrency', 'amount', 'proof_content', 'proof_type', 'created_at']
        return []  # Adding new deposit - all fields editable
    
    def save_model(self, request, obj, form, change):
        """Override save to update user balance when deposit is approved."""
        # Check if this is a new deposit being saved as approved
        if not change and obj.status == 'approved':
            # New deposit being created with 'approved' status
            obj.approved_at = timezone.now()
            obj.approved_by = request.user
            obj.save()
            
            # Update user balance
            user = obj.user
            user.balance += obj.amount
            user.save()
        
        # Check if status changed from non-approved to approved
        elif change:  # Editing existing deposit
            if form.has_changed() and 'status' in form.changed_data:
                old_status = Deposit.objects.get(pk=obj.pk).status
                if old_status != 'approved' and obj.status == 'approved':
                    # Status being changed to approved
                    obj.approved_at = timezone.now()
                    obj.approved_by = request.user
                    obj.save()
                    
                    # Update user balance
                    user = obj.user
                    user.balance += obj.amount
                    user.save()
                else:
                    # Just save normally if status didn't change to approved
                    obj.save()
            else:
                obj.save()
        else:
            obj.save()
    
    def approve_deposit(self, request, queryset):
        """Admin action to approve deposits."""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        approved_count = 0
        for deposit in queryset.filter(status='pending'):
            deposit.status = 'approved'
            deposit.approved_at = timezone.now()
            deposit.approved_by = request.user
            deposit.save()  # This will trigger save_model which sends the email
            
            approved_count += 1
        
        self.message_user(request, f'{approved_count} deposit(s) approved successfully and emails sent.')
    
    approve_deposit.short_description = 'Approve selected deposits'
    
    def reject_deposit(self, request, queryset):
        """Admin action to reject deposits."""
        rejected_count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{rejected_count} deposit(s) rejected.')
    
    reject_deposit.short_description = 'Reject selected deposits'
