from .models import CarMake, CarModel

def initiate():

    car_make_data = [
        {"name": "NISSAN",   "description": "Great cars. Japanese technology"},
        {"name": "Mercedes", "description": "Great cars. German technology"},
        {"name": "Audi",     "description": "Great cars. German technology"},
        {"name": "Kia",      "description": "Great cars. Korean technology"},
        {"name": "Toyota",   "description": "Great cars. Japanese technology"},
    ]
    makes = [CarMake.objects.create(**d) for d in car_make_data]

    dealer_id_by_make = {
        "NISSAN": 1,
        "Mercedes": 2,
        "Audi": 3,
        "Kia": 4,
        "Toyota": 5,
    }

    car_model_data = [
        {"name": "Pathfinder", "type": "SUV",   
        "year": 2023, "car_make": makes[0]},
        {"name": "Qashqai",    "type": "SUV",   
        "year": 2023, "car_make": makes[0]},
        {"name": "XTRAIL",     "type": "SUV",   
        "year": 2023, "car_make": makes[0]},

        {"name": "A-Class",    "type": "SUV",   
        "year": 2023, "car_make": makes[1]},
        {"name": "C-Class",    "type": "SUV",   
        "year": 2023, "car_make": makes[1]},
        {"name": "E-Class",    "type": "SUV",   
        "year": 2023, "car_make": makes[1]},

        {"name": "A4",         "type": "SUV",   
        "year": 2023, "car_make": makes[2]},
        {"name": "A5",         "type": "SUV",   
        "year": 2023, "car_make": makes[2]},
        {"name": "A6",         "type": "SUV",   
        "year": 2023, "car_make": makes[2]},

        {"name": "Sorrento",   "type": "SUV",   
        "year": 2023, "car_make": makes[3]},
        {"name": "Carnival",   "type": "SUV",   
        "year": 2023, "car_make": makes[3]},
        {"name": "Cerato",     "type": "Sedan", 
        "year": 2023, "car_make": makes[3]},

        {"name": "Corolla",    "type": "Sedan", 
        "year": 2023, "car_make": makes[4]},
        {"name": "Camry",      "type": "Sedan", 
        "year": 2023, "car_make": makes[4]},
        {"name": "Kluger",     "type": "SUV",   
        "year": 2023, "car_make": makes[4]},
    ]

    for d in car_model_data:
        make = d["car_make"]
        dealer_id = dealer_id_by_make.get(make.name, 1)
        CarModel.objects.create(
            name=d["name"],
            type=d["type"],
            year=d["year"],
            car_make=make,
            dealer_id=dealer_id,   
        )
