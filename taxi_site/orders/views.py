import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .data import drivers_sorted, random_eta
from .utils import send_order_to_telegram


@require_GET
def index(request: HttpRequest) -> HttpResponse:
    drivers = [
        {
            "id": d.id,
            "full_name": d.full_name,
            "car": d.car,
            "phone": d.phone,
            "price": d.price,
            "eta": random_eta(),
        }
        for d in drivers_sorted()
    ]
    context = {
        "drivers": drivers,
    }
    return render(request, "orders/index.html", context)


@require_GET
def api_drivers(request: HttpRequest) -> JsonResponse:
    drivers = [
        {
            "id": d.id,
            "full_name": d.full_name,
            "car": d.car,
            "phone": d.phone,
            "price": d.price,
            "eta": random_eta(),
        }
        for d in drivers_sorted()
    ]
    return JsonResponse({"drivers": drivers})


@csrf_exempt
@require_POST
def api_order(request: HttpRequest) -> JsonResponse:
    data = json.loads(request.body or "{}")
    driver_id = data.get("driver_id")
    origin = data.get("origin", "")
    destination = data.get("destination", "")
    payment = data.get("payment", "naqd")
    note = data.get("note", "")

    driver = next((d for d in drivers_sorted() if d.id == driver_id), None)
    if not driver:
        return JsonResponse({"error": "Haydovchi topilmadi."}, status=400)

    eta = random_eta()
    telegram_err = send_order_to_telegram(
        driver=driver,
        origin=origin,
        destination=destination,
        payment="Naqd" if payment == "naqd" else "Karta",
        note=note,
        eta_minutes=eta,
    )

    return JsonResponse(
        {
            "ok": True,
            "eta": eta,
            "telegram_forwarded": telegram_err is None,
            "telegram_error": telegram_err,
        }
    )
