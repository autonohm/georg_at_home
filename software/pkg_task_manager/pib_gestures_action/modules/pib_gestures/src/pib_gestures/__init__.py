#from pib_gestures.locate_object import locate_object
#from pib_gestures.point_to import point_to
#from pib_gestures.greet_person import greet_person
#from pib_gestures.look_at import look_at
#from pib_gestures.offer_hand import offer_hand
#from pib_gestures.open_hand import open_hand
#from pib_gestures.close_hand import close_hand

__version__ = "1.0.0"

__all__ = [
    "locate_object",
    "point_to",
    "greet_person",
    "look_at",
    "offer_hand",
    "open_hand",
    "close_hand"
]


def __getattr__(name):
    if name == "locate_object":
        from .locate_object import locate_object
        return locate_object

    if name == "point_to":
        from .point_to import point_to
        return point_to

    if name == "greet_person":
        from .greet_person import greet_person
        return greet_person

    if name == "look_at":
        from .look_at import look_at
        return look_at

    if name == "offer_hand":
        from .offer_hand import offer_hand
        return offer_hand
        
    if name == "open_hand":
        from .open_hand import open_hand
        return open_hand
        
    if name == "close_hand":
        from .close_hand import close_hand
        return close_hand
        
    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
