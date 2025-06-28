

# Backend Devleoper Task - FreJun

## How to run: 

- install docker
- cd `booker`
- run `docker compose up`9 AM - 10 AM

## Unique Selling Points:

⭐ Double booking is prevent by using `select_for_update()` and placing the booking logic under a `transaction` block

⭐ Lean and readable Views 

⭐ Pagination for potentially big responses under `list bookings`

⭐ Use of pydantic to increase type safety

⭐ Role based accesss - Admins have the ability to cancel other user's bookings


## Assumptions:

- Admins can cancel bookings made by other users
- Teams can only book a conference room
- Children aren't considered to occupy a room when they book one - only when an adult takes it, it is considered occupied.

## Database:

- SQLite is used for now, as it seemed the most simple one to get this task done.

```
    # Schema

    Team {
        name: text
    }

    User {
        name: text,
        age: int, 
        gender: str,
        is_admin: bool,
        team: int (foreign key)
    }

    Slot {
        slot_time: str (ex: 9 AM - 10 AM)
    }

    Room {
        room_type: str 
        room_nos: int
        capacity: int
    }

    Bookings {
        timestamp: date
        slot: int (foreign key)
        room: int (foreign key)
        booked_by: int 
        user_type: "USER" | "TEAM"
    }
```

- `booked_by` under Bookings is not a foreign key to `User` model because then we wont be able to map team with the records. We also use `user_type` as a discriminator between them. 

## Endpoints:

### List bookings placed datewise:

`GET http://0.0.0.0:8000/api/v1/bookings/?date=2025-06-28`

- Assumption: Listing bookings all-time would be pointless, therefore taking a date which can be used to list bookings for that particular date.

- Response

```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 27,
            "booked_by": {
                "id": 3,
                "name": "Eric",
                "age": 30,
                "gender": "MALE",
                "is_admin": false,
                "team": 1
            },
            "room": {
                "id": 1,
                "room_type": "PRIVATE ROOM",
                "room_nos": 8,
                "capacity": 1
            },
            "timestamp": "2025-06-28",
            "user_type": "USER",
            "slot": 7
        },
        {
            "id": 28,
            "booked_by": {
                "id": 4,
                "name": "Matthew",
                "age": 32,
                "gender": "MALE",
                "is_admin": false,
                "team": 1
            },
            "room": {
                "id": 1,
                "room_type": "PRIVATE ROOM",
                "room_nos": 8,
                "capacity": 1
            },
            "timestamp": "2025-06-28",
            "user_type": "USER",
            "slot": 7
        }
    ]
}
```

### Get available for a slot in a day

`GET http://0.0.0.0:8000/api/v1/bookings/available?slot=3 PM - 4 PM&date=2025-06-28`

- `date` is optional, if not sent then the current server time is chosen as default
- Response

```
{
    "PRIVATE ROOM": 6,
    "CONFERENCE_ROOM": 4,
    "SHARED_DESK": 12
}
```

### Book a room:

`POST http://0.0.0.0:8000/api/v1/bookings/`

```
Request body:
{
    "slot": "3 PM - 4 PM",
    "room_id": 1,
    "booked_by": 2,
    "user_type": "USER",
    "booking_date": "2025-06-28"
}
```

- room_id varies from 1-3, 1 --> private room, 2 --> conference room, 3 --> shared_desk

- Response
```
{
    "id": 26,
    "booked_by": {
        "id": 2,
        "name": "Reshma",
        "age": 25,
        "gender": "FEMALE",
        "is_admin": true,
        "team": 1
    },
    "room": {
        "id": 1,
        "room_type": "PRIVATE ROOM",
        "room_nos": 8,
        "capacity": 1
    },
    "timestamp": "2025-06-28",
    "user_type": "USER",
    "slot": 7
}
```

### Cancel a room:

`DELETE http://0.0.0.0:8000/api/v1/bookings/{booking_id}/`

```
Request body:

{
    user_id: 8
}
```

```
Response 204 No Content
```


