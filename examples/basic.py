# stdlib import
from typing import Protocol

# pip import
from typed_event import Event


# =============================================================================
# Define the callback type
# =============================================================================
class UserLoginCallback(Protocol):
    def __call__(self, username: str, user_id: int) -> None: ...

# =============================================================================
# Define the event with the callback type 
# =============================================================================

# Create an instance of our Event, typed with the protocol.
on_user_login = Event[UserLoginCallback]()

# =============================================================================
# 2 examples of event callback
# =============================================================================

def welcome_user(username: str, user_id: int) -> None:
    print(f"Welcome, {username}! Your user ID is {user_id}.")

def log_login_event(username: str, user_id: float) -> None:
    print(f"[{username}] logged in with ID [{user_id}] at the database level.")

# =============================================================================
# Connect the event to the 2 callback
# =============================================================================
on_user_login.subscribe(welcome_user)
on_user_login.subscribe(log_login_event)


# =============================================================================
# Dispatch the event
# =============================================================================
print("Dispatching event for user 'Alice'...")
# FIXME this line should raise a mypy error because of wrong type for user_id
on_user_login.dispatch("Alice", "ddd")
