
from room.models import Slot, Room, User, Team

for time in Slot.SlotChoices.choices:
    Slot.objects.get_or_create(
        slot_time = time[0]
    )

Room.objects.get_or_create(
    room_type=Room.RoomTypeChoices.private_room.value,
    capacity=1,
    room_nos=8   
)

room = Room.objects.get_or_create(
    room_type=Room.RoomTypeChoices.conference_room.value,
    capacity=3,
    room_nos=4
)[0]

room.capacity = 1
room.save()

Room.objects.get_or_create(
    room_type=Room.RoomTypeChoices.shared_desk.value,
    capacity=4,
    room_nos=3
)

User.objects.get_or_create(
    name="Rahul",
    age=9,
    gender=User.GenderChoices.MALE.value,
    is_admin=False,
    team=None
)

team = Team.objects.get_or_create(
    name="Customer Success"
)
team = team[0]

User.objects.get_or_create(
    name="Reshma",
    age=25,
    gender=User.GenderChoices.FEMALE.value,
    is_admin=True,
    team=team
)

User.objects.get_or_create(
    name="Eric",
    age=30,
    gender=User.GenderChoices.MALE.value,
    is_admin=False,
    team=team
)

User.objects.get_or_create(
    name="Matthew",
    age=32,
    gender=User.GenderChoices.MALE.value,
    is_admin=False,
    team=team
)

User.objects.get_or_create(
    name="Robert",
    age=45,
    gender=User.GenderChoices.MALE.value,
    is_admin=False,
    team=team
)
