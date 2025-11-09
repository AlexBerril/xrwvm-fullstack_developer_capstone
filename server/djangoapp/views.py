# Uncomment the required imports before adding the code

import json
import logging
from urllib.parse import quote

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import analyze_review_sentiments, get_request, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    payload = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        payload = {"userName": username, "status": "Authenticated"}
    return JsonResponse(payload)


# Create a `logout_request` view to handle sign out request
def logout_user(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    logout(request)
    return JsonResponse({"userName": ""})


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    username_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except Exception:
        # If not, simply log this is a new user
        logger.debug("%s is new user", username)

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        # Login the user and redirect to list page
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"userName": username, "error": "Already Registered"})


# Update the `get_dealerships` view to render the index page with
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    try:
        # 1) забираем отзывы из бэкенда
        reviews_payload = get_request(f"/fetchReviews/dealer/{int(dealer_id)}")

        # ожидаемый формат — список словарей с полем "review" (и др.)
        reviews = (
            reviews_payload
            if isinstance(reviews_payload, list)
            else reviews_payload.get("reviews", [])
        )

        # 2) для каждого отзыва дергаем сервис тональности
        enriched = []
        for r in reviews:
            text = str(r.get("review", "")).strip()
            sentiment = "neutral"  # дефолт на случай сетевой ошибки
            if text:
                try:
                    # URL-кодируем текст, т.к. микросервис ожидает текст в пути
                    analysis = analyze_review_sentiments(quote(text))
                    # обычно возвращается {"sentiment": "..."}
                    if isinstance(analysis, dict) and analysis.get("sentiment"):
                        sentiment = analysis["sentiment"]
                except Exception:
                    pass
            rd = dict(r)  # копия исходного словаря с отзывом
            rd["sentiment"] = sentiment
            enriched.append(rd)

        return JsonResponse(
            {"status": 200, "dealer_id": int(dealer_id), "reviews": enriched}
        )
    except Exception as exc:
        return JsonResponse(
            {"status": 500, "message": f"Internal Error: {exc}"}, status=500
        )


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    try:
        endpoint = f"/fetchDealer/{int(dealer_id)}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    except Exception as exc:
        return JsonResponse(
            {"status": 500, "message": f"Internal Error: {exc}"}, status=500
        )


# Create an `add_review` view to submit a review
def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append(
            {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        )
    return JsonResponse({"CarModels": cars})
