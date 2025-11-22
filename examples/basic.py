# 
from typing import Protocol


from typed_event import Event


# We can define the expected function signature using a Protocol for clarity.
class UserLoginCallback(Protocol):
    def __call__(self, username: str, user_id: int) -> None: ...

# Create an instance of our Event, typed with the protocol.
on_user_login = Event[UserLoginCallback]()

def welcome_user(username: str, user_id: int) -> None:
    print(f"Welcome, {username}! Your user ID is {user_id}.")

def log_login_event(username: str, user_id: float) -> None:
    print(f"[{username}] logged in with ID [{user_id}] at the database level.")

# Subscribe the functions
on_user_login.subscribe(welcome_user)
on_user_login.subscribe(log_login_event)

# Dispatch the event
print("Dispatching event for user 'Alice'...")
on_user_login.dispatch("Alice", "ddd")
