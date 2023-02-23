from django.contrib import admin
from finance_majordomo.transactions.models import Transaction

class TasksTransactionsInline(admin.TabularInline):
    model = Transaction
    extra = 1
    # list_display = ('id', 'task', 'label')
    # list_display_links = ('id', 'task', 'label')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_display_links = ('id', )


admin.site.register(Transaction, TransactionAdmin)
