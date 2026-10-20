"""Exact amounts and queries scoped to the current browser session and month."""

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from main.models import Budget, Expense

from .assistant import text


def money(value, allow_zero=False):
    if isinstance(value, bool) or value is None:
        raise ValueError("Enter a valid amount.")
    try:
        result = Decimal(str(value))
        if (
            not result.is_finite()
            or result < 0
            or (result == 0 and not allow_zero)
            or result >= Decimal("100000000")
            or result.as_tuple().exponent < -2
        ):
            raise ValueError(
                "Use a positive amount below 100000000 with at most two decimal places."
            )
        return result.quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Enter a valid amount.") from exc


def scope(request):
    if not request.session.session_key:
        request.session.create()
    return {
        "session_id": request.session.session_key,
        "month": timezone.localdate().strftime("%Y-%m"),
    }


def snapshot(query):
    expenses = Expense.objects.filter(**query)
    total = expenses.aggregate(value=Sum("amount"))["value"] or Decimal("0.00")
    budget = Budget.objects.filter(**query).first()
    categories = expenses.values("category").annotate(amount=Sum("amount")).order_by("category")
    return {
        "month": query["month"],
        "currency": "NPR",
        "budget": str(budget.amount) if budget else None,
        "total": f"{total:.2f}",
        "remaining": f"{budget.amount - total:.2f}" if budget else None,
        "exceeded": bool(budget and total > budget.amount),
        "expenses": [
            {
                "id": x.id,
                "category": x.category,
                "amount": str(x.amount),
                "created_at": x.created_at.isoformat(),
            }
            for x in expenses
        ],
        "categories": [{"category": x["category"], "amount": str(x["amount"])} for x in categories],
    }


def process(request, data=None):
    query = scope(request)
    if data is not None:
        with transaction.atomic():
            action = data.get("action")
            if action == "add":
                Expense.objects.create(
                    **query,
                    category=text(data.get("category"), "Category", 64),
                    amount=money(data.get("amount")),
                )
            elif action == "budget":
                Budget.objects.update_or_create(
                    **query, defaults={"amount": money(data.get("amount"), allow_zero=True)}
                )
            elif action == "delete":
                pk = data.get("id")
                if isinstance(pk, bool) or not isinstance(pk, int) or pk < 1:
                    raise ValueError("Choose a valid expense.")
                deleted, _ = Expense.objects.filter(**query, pk=pk).delete()
                if not deleted:
                    raise LookupError("Expense not found in this browser session.")
            elif action == "reset":
                Expense.objects.filter(**query).delete()
                Budget.objects.filter(**query).delete()
            else:
                raise ValueError("Choose add, budget, delete or reset.")
    return snapshot(query)
