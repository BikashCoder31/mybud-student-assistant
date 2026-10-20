from django.db import models


class Expense(models.Model):
    session_id = models.CharField(max_length=40, db_index=True)
    month = models.CharField(max_length=7, db_index=True)
    category = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="expense_positive")
        ]

    def __str__(self):
        return f"{self.category}: {self.amount}"


class Budget(models.Model):
    session_id = models.CharField(max_length=40)
    month = models.CharField(max_length=7)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_set = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_id", "month"], name="one_budget_per_session_month"
            ),
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="budget_nonnegative"),
        ]

    def __str__(self):
        return f"Budget: {self.amount}"
