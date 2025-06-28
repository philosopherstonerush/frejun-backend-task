from django.db import transaction, IntegrityError
from pydantic import BaseModel
from .models import Bookings, Slot, Room, Team, User

class BookParameters(BaseModel):
    slot: str
    room_id: int 
    booked_by: int
    user_type: str
    booking_date: str

class BookingError(BaseModel):
    error_message: str

class RoomBookingService():

    @transaction.atomic
    def book(self, data: BookParameters) -> Bookings | BookingError:

        room = Room.objects.get(pk=data.room_id)
        slot = Slot.objects.get(slot_time=data.slot)

        if room.room_type == Room.RoomTypeChoices.private_room.value:
            if not data.user_type == Bookings.UserTypeChoices.user.value:
                return BookingError(
                    error_message="Teams cannot book a private room"
                ) 

            if Bookings.objects.select_for_update().filter(
                room=room,slot=slot,timestamp=data.booking_date,booked_by__in=User.objects.filter(age__gte=10)
            ).count() >= room.room_nos:
                return BookingError(
                    error_message="Slot is already booked"
                )
        
        if room.room_type == Room.RoomTypeChoices.conference_room.value:
            if not data.user_type == Bookings.UserTypeChoices.team.value:
                return BookingError(
                    error_message="users cannot book a conference room"
                ) 

            if User.objects.select_for_update().filter(team_id=data.booked_by).count() <= 3: 
                return BookingError(
                    error_message="A team can only book a conference room if it has more than 3 associated members"
                )
            
            if Bookings.objects.select_for_update().filter(
                room=room, slot=slot, timestamp=data.booking_date
            ).count() >= room.room_nos * room.capacity:
                return BookingError(
                    error_message="All conference rooms are occupied at the moment"
                )
        
        if room.room_type == Room.RoomTypeChoices.shared_desk.value:
            
            if not data.user_type == Bookings.UserTypeChoices.user.value:
                return BookingError(
                    error_message="teams cannot book a shared desk"
                )
            
            if Bookings.objects.select_for_update().filter(
                room=room,slot=slot,timestamp=data.booking_date, booked_by__in=User.objects.filter(age__gte=10)
            ).count() >= room.room_nos * room.capacity: 
                return BookingError(
                    "This room is already at max occupancy for this slot"
                )

        try: 
            return Bookings.objects.get_or_create(
                slot=slot,
                room=room,
                timestamp=data.booking_date,
                user_type=data.user_type,
                booked_by=data.booked_by
            )[0]
        except IntegrityError as e:
            return BookingError(
                error_message="Room is already booked"
            )
    
    def cancel(self, booking_id: int, user_id: int) -> None | BookingError:
        user = User.objects.get(pk=user_id)
        booking = Bookings.objects.get(pk=booking_id)

        if (booking.booked_by != user_id) and (not user.is_admin):
            return BookingError(
                error_message="Unauthorized cancellation of a room by another user"
            )
        
        booking.delete()

    def check_availability(self, room_type: str, slot: str, date_field: str):
        room = Room.objects.get(room_type=room_type)
        slot = Slot.objects.get(slot_time=slot)

        if room_type == Room.RoomTypeChoices.shared_desk.value:
            if Bookings.objects.filter(
                room=room,slot=slot,timestamp=date_field, booked_by__in=User.objects.filter(age__gte=10)
            ).count() >= room.room_nos * room.capacity: 
                return False
        else: 
            if Bookings.objects.filter(
                room=room, slot=slot, timestamp=date_field
            ).count() >= room.room_nos * room.capacity:
                return False
            
        return True
    
    def fetch_available_rooms(self, slot: str, date_field: str):
        slot = Slot.objects.get(slot_time=slot)
        rooms = Room.objects.all()
        available_rooms = dict()

        for room in rooms:

            occupied_cnt = Bookings.objects.filter(
                room=room, slot=slot, timestamp=date_field
            ).count()

            child_cnt = Bookings.objects.filter(
                room=room, slot=slot, timestamp=date_field, user_type=Bookings.UserTypeChoices.user.value,
                booked_by__in=User.objects.filter(age__lte=10)
            ).count()

            # Remove all children occupying a room
            total = occupied_cnt - child_cnt

            available_rooms.update({
                room.room_type: (room.room_nos * room.capacity) - total
            })

        return available_rooms