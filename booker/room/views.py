from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import request
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import serializers
from datetime import date
from rest_framework.response import Response
from rest_framework import status
from django.db.models import OuterRef, Subquery
from .models import Bookings, User, Team, Slot, Room
from .services import RoomBookingService, BookingError, BookParameters

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model=Team
        fields='__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields='__all__'

class BookRoomSerializer(ModelSerializer):
    booked_by = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model= Bookings
        fields='__all__'

    def get_booked_by(self, obj):
        if obj.user_type == Bookings.UserTypeChoices.user.value: 
            serializer = UserSerializer(User.objects.get(pk=obj.booked_by))
            return serializer.data
        else:
            serializer = TeamSerializer(Team.objects.get(pk=obj.booked_by))
            return serializer.data
    
    def get_room(self, obj):
        serializer = RoomSerializer(obj.room)
        return serializer.data

class CreateBookRoomRequestSerializer(Serializer):
    slot = serializers.ChoiceField(choices=Slot.SlotChoices.choices)
    room_id = serializers.IntegerField()
    booked_by = serializers.IntegerField()
    user_type = serializers.ChoiceField(choices=Bookings.UserTypeChoices.choices)
    booking_date = serializers.DateField(input_formats=['%Y-%m-%d'])

    def validate(self, data):
        user_type = data["user_type"]
        if user_type == Bookings.UserTypeChoices.user.value:
            if not User.objects.filter(pk=data["booked_by"]).exists():
                raise ValidationError("User of this id doesn't exist")
        else:
            if not Team.objects.filter(pk=data["booked_by"]).exists():
                raise ValidationError("Team is of this id doesn't exist")
            
        if data["booking_date"] < date.today():
            raise ValidationError("Cannot book for a date prior than today")
    
        return data
    
class DeleteBookRoomRequestSerializer(Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        if not User.objects.filter(pk=data["user_id"]).exists():
            raise ValidationError("Specified user doesn't exist")
        return data    

class CustomPagination(PageNumberPagination):
    page_size=5
    page_size_query_param = "page_size"
    max_page_size = 1000

class BookRoomView(viewsets.ModelViewSet):

    pagination_class = CustomPagination
    
    def create(self, request):
        serializer = CreateBookRoomRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data["booking_date"] = str(validated_data["booking_date"])
        bookingService = RoomBookingService()

        result = bookingService.book(BookParameters(**validated_data))
        
        if isinstance(result, BookingError):
            return Response(result.model_dump_json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            response_serializer = BookRoomSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        
        if not Bookings.objects.filter(pk=pk).exists():
            return Response(BookingError(
                error_message="Invalid Booking id"
            ).model_dump_json(), status=status.HTTP_400_BAD_REQUEST)

        serializer = DeleteBookRoomRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        bookingService = RoomBookingService()

        result = bookingService.cancel(booking_id=pk, user_id=validated_data["user_id"])

        if isinstance(result, BookingError):
            return Response(
                result.model_dump_json(), status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        
        queryset = Bookings.objects.all().select_related(
            "room", "slot"
        )

        if date_field := request.query_params.get('date'):
            queryset = queryset.filter(timestamp=date_field)
        else:
            return Response(
                BookingError(
                    error_message="Provide a date to list bookings"
                ).model_dump_json()
            )
        
        queryset = queryset.order_by("slot")

        page = self.paginate_queryset(queryset)
        if page is not None:
            response_serializer = BookRoomSerializer(page, many=True)
            return self.get_paginated_response(response_serializer.data)
        
        serializer = BookRoomSerializer(queryset, many=True)

        return self.get_paginated_response(serializer.data)
        
    @action(methods=['get'], detail=False, url_path="available")
    def available_rooms_per_slot(self, request):

        slot = request.query_params.get("slot")
        date_field = request.query_params.get("date")

        if date_field == None:
            date_field = date.today()

        if slot == None:
            return Response(BookingError(
                            error_message="slot must be sent to find out available rooms"
            ).model_dump_json(), status=status.HTTP_400_BAD_REQUEST)
        
        bookingService = RoomBookingService()

        rooms_available = bookingService.fetch_available_rooms(
            slot, date_field
        )

        return Response(rooms_available, status=status.HTTP_200_OK)