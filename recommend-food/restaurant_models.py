from typing import List, Optional, Dict, Any

class Restaurant:
    """
    A class to represent basic restaurant data from search results.
    
    Attributes:
        name (str): Name of the restaurant
        place_id (str): Google Places ID for the restaurant
        open_now (bool): Whether the restaurant is currently open (may be None if unknown)
        rating (float): Rating of the restaurant (0.0-5.0)
    """
    def __init__(self, name: str, place_id: str, open_now: Optional[bool], rating: float):
        self.name = name
        self.place_id = place_id
        self.open_now = open_now
        self.rating = rating
        
    def __str__(self) -> str:
        return f"Restaurant(name='{self.name}',place_id='{self.place_id}', open_now={self.open_now}, rating={self.rating})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the restaurant object to a dictionary for serialization"""
        return {
            "name": self.name,
            "place_id": self.place_id,
            "open_now": self.open_now,
            "rating": self.rating
        }
        
    @classmethod
    def from_google_place(cls, place_data: Dict[str, Any]) -> 'Restaurant':
        """Create a Restaurant object from Google Places API response data"""
        name = place_data.get("name", "")
        place_id = place_data.get("place_id", "")
        open_now = place_data.get("opening_hours", {}).get("open_now")
        rating = place_data.get("rating", 0.0)
        
        return cls(name, place_id, open_now, rating)


class RestaurantDetail:
    """
    A class to represent detailed restaurant information.
    
    Attributes:
        name (str): Name of the restaurant
        formatted_address (str): Formatted address of the restaurant (Korean)
        weekday_text (List[str]): Opening hours for each day of the week
        rating (float): Rating of the restaurant (0.0-5.0)
        user_ratings_total (int): Total number of user ratings
        price_level (int): Price level of the restaurant (0-4)
    """
    def __init__(self, 
                 name: str, 
                 formatted_address: str, 
                 weekday_text: Optional[List[str]],
                 rating: Optional[float] = None,
                 user_ratings_total: Optional[int] = None,
                 price_level: Optional[int] = None):
        self.name = name
        self.formatted_address = formatted_address
        self.weekday_text = weekday_text if weekday_text else []
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.price_level = price_level
        
    def __str__(self) -> str:
        return f"RestaurantDetail(name='{self.name}', address='{self.formatted_address}',weekday_text='{self.weekday_text}', rating={self.rating})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the restaurant detail object to a dictionary for serialization"""
        return {
            "name": self.name,
            "formatted_address": self.formatted_address,
            "weekday_text": self.weekday_text,
            "rating": self.rating,
            "user_ratings_total": self.user_ratings_total,
            "price_level": self.price_level
        }
        
    @classmethod
    def from_google_place_details(cls, detail_data: Dict[str, Any]) -> 'RestaurantDetail':
        """Create a RestaurantDetail object from Google Places Details API response data"""
        name = detail_data.get("name", "")
        formatted_address = detail_data.get("formatted_address", "")
        weekday_text = detail_data.get("opening_hours", {}).get("weekday_text")
        rating = detail_data.get("rating")
        user_ratings_total = detail_data.get("user_ratings_total")
        price_level = detail_data.get("price_level")
        
        return cls(name, formatted_address, weekday_text, rating, user_ratings_total, price_level) 