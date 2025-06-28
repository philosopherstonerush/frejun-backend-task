from django.db import models

class Team(models.Model):
    name = models.TextField(blank=True)

class User(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "MALE"
        FEMALE = "FEMALE"

    name = models.TextField(blank=False, null=False)
    age = models.IntegerField()
    gender = models.TextField(choices=GenderChoices.choices)
    is_admin = models.BooleanField(default=False)
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL)

class Slot(models.Model):
    class SlotChoices(models.TextChoices):
        NINE_AM_TEN_AM = "9 AM - 10 AM"
        TEN_AM_ELEVEN_AM = "10 AM - 11 AM"
        ELEVEN_AM_TWELVE_PM = "11 AM - 12 PM"
        TWELVE_PM_ONE_PM = "12 PM - 1 PM"
        ONE_PM_TWO_PM = "1 PM - 2 PM"
        TWO_PM_THREE_PM = "2 PM - 3 PM"
        THREE_PM_FOUR_PM = "3 PM - 4 PM"
        FOUR_PM_FIVE_PM = "4 PM - 5 PM"
        FIVE_PM_SIX_PM = "5 PM - 6 PM"

    slot_time = models.TextField(choices=SlotChoices.choices)

class Room(models.Model):
    class RoomTypeChoices(models.TextChoices):
        private_room = "PRIVATE ROOM"
        conference_room = "CONFERENCE_ROOM"
        shared_desk = "SHARED_DESK"

    room_type = models.TextField(choices=RoomTypeChoices.choices)
    room_nos = models.IntegerField()
    capacity = models.IntegerField()

class Bookings(models.Model):
    class UserTypeChoices(models.TextChoices):
        user = "USER"
        team = "TEAM"

    timestamp = models.DateField(auto_now_add=True)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booked_by = models.BigIntegerField(null=False)
    user_type = models.TextField(choices=UserTypeChoices.choices)