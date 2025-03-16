# Class used to define Users
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from geopy import Nominatim, Location


# class AddressBase(SQLModel):
#     street: str
#     city: str
#     postal_code: str
#     country: str
#
#
# class Address(AddressBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     latitude: Optional[float] = Field(default=None)
#     longitude: Optional[float] = Field(default=None)
#     user_id: Optional[int] = Field(default=None, foreign_key="user.id")
#     user: "User" = Relationship(back_populates="address")
#
#
# class AddressUpdate(SQLModel):
#     street: str | None
#     city: str | None
#     postal_code: str | None
#     country: str | None


class UserBase(SQLModel):
    first_name: str
    last_name: str
    date_of_birth: date
    street: str
    city: str
    postal_code: str
    country: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None
    street: str | None
    city: str | None
    postal_code: str | None
    country: str | None


class UserResponse(UserBase):
    id: int
    latitude: float | None
    longitude: float | None


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    accounts: list["Account"] = Relationship(back_populates="user")

    def calculate_lat_long(self):
        geolocator = Nominatim(user_agent="user_address_locator")
        address_str = f"{self.street}, {self.city}, {self.postal_code}, {self.country}"
        try:
            location: Location = geolocator.geocode(address_str)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
            else:
                self.latitude = None
                self.longitude = None
        except Exception as e:
            print(f"Error geocoding address: {e}")
            self.latitude = None
            self.longitude = None
