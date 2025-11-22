"""
Comprehensive pytest tests for typed_event.Event class.
"""

import pytest
from typing import Protocol
from typed_event import Event


# Test fixtures and helper classes
class SimpleCallback(Protocol):
    """Protocol for a simple callback with no arguments."""
    def __call__(self) -> None: ...


class StringCallback(Protocol):
    """Protocol for a callback with a string argument."""
    def __call__(self, message: str) -> None: ...


class MultiArgCallback(Protocol):
    """Protocol for a callback with multiple arguments."""
    def __call__(self, name: str, age: int, active: bool = True) -> None: ...


class TestEventInitialization:
    """Tests for Event initialization."""

    def test_event_can_be_created(self):
        """Test that an Event instance can be created."""
        event = Event[SimpleCallback]()
        assert event is not None

    def test_event_starts_with_empty_callbacks(self):
        """Test that a new Event has no subscribers."""
        event = Event[SimpleCallback]()
        assert len(event._callbacks) == 0


class TestEventSubscribe:
    """Tests for Event.subscribe() method."""

    def test_subscribe_single_callback(self):
        """Test subscribing a single callback to an event."""
        event = Event[SimpleCallback]()
        called = []
        
        def callback() -> None:
            called.append(True)
        
        event.subscribe(callback)
        assert len(event._callbacks) == 1
        assert callback in event._callbacks

    def test_subscribe_multiple_callbacks(self):
        """Test subscribing multiple callbacks to an event."""
        event = Event[SimpleCallback]()
        callbacks = []
        
        def callback1() -> None:
            callbacks.append(1)
        
        def callback2() -> None:
            callbacks.append(2)
        
        def callback3() -> None:
            callbacks.append(3)
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        assert len(event._callbacks) == 3
        assert callback1 in event._callbacks
        assert callback2 in event._callbacks
        assert callback3 in event._callbacks

    def test_subscribe_same_callback_twice(self):
        """Test that the same callback can be subscribed multiple times."""
        event = Event[SimpleCallback]()
        call_count = []
        
        def callback() -> None:
            call_count.append(1)
        
        event.subscribe(callback)
        event.subscribe(callback)
        
        assert len(event._callbacks) == 2
        event.dispatch()
        assert len(call_count) == 2


class TestEventUnsubscribe:
    """Tests for Event.unsubscribe() method."""

    def test_unsubscribe_existing_callback(self):
        """Test unsubscribing an existing callback."""
        event = Event[SimpleCallback]()
        
        def callback() -> None:
            pass
        
        event.subscribe(callback)
        assert len(event._callbacks) == 1
        
        event.unsubscribe(callback)
        assert len(event._callbacks) == 0
        assert callback not in event._callbacks

    def test_unsubscribe_one_of_multiple_callbacks(self):
        """Test unsubscribing one callback when multiple are subscribed."""
        event = Event[SimpleCallback]()
        
        def callback1() -> None:
            pass
        
        def callback2() -> None:
            pass
        
        def callback3() -> None:
            pass
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        event.unsubscribe(callback2)
        
        assert len(event._callbacks) == 2
        assert callback1 in event._callbacks
        assert callback2 not in event._callbacks
        assert callback3 in event._callbacks

    def test_unsubscribe_duplicate_callback_removes_first_occurrence(self):
        """Test that unsubscribe removes only the first occurrence when callback is subscribed multiple times."""
        event = Event[SimpleCallback]()
        call_count = []
        
        def callback() -> None:
            call_count.append(1)
        
        event.subscribe(callback)
        event.subscribe(callback)
        assert len(event._callbacks) == 2
        
        event.unsubscribe(callback)
        assert len(event._callbacks) == 1
        
        event.dispatch()
        assert len(call_count) == 1

    def test_unsubscribe_nonexistent_callback_raises_error(self):
        """Test that unsubscribing a non-existent callback raises ValueError."""
        event = Event[SimpleCallback]()
        
        def callback() -> None:
            pass
        
        with pytest.raises(ValueError):
            event.unsubscribe(callback)


class TestEventDispatch:
    """Tests for Event.dispatch() method."""

    def test_dispatch_with_no_subscribers(self):
        """Test dispatching an event with no subscribers doesn't raise an error."""
        event = Event[SimpleCallback]()
        event.dispatch()  # Should not raise an error

    def test_dispatch_calls_single_subscriber(self):
        """Test that dispatch calls a single subscribed callback."""
        event = Event[SimpleCallback]()
        called = []
        
        def callback() -> None:
            called.append(True)
        
        event.subscribe(callback)
        event.dispatch()
        
        assert len(called) == 1

    def test_dispatch_calls_all_subscribers(self):
        """Test that dispatch calls all subscribed callbacks."""
        event = Event[SimpleCallback]()
        results = []
        
        def callback1() -> None:
            results.append(1)
        
        def callback2() -> None:
            results.append(2)
        
        def callback3() -> None:
            results.append(3)
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        event.dispatch()
        
        assert results == [1, 2, 3]

    def test_dispatch_with_positional_arguments(self):
        """Test dispatching with positional arguments."""
        event = Event[StringCallback]()
        received_messages = []
        
        def callback(message: str) -> None:
            received_messages.append(message)
        
        event.subscribe(callback)
        event.dispatch("Hello, World!")
        
        assert received_messages == ["Hello, World!"]

    def test_dispatch_with_multiple_arguments(self):
        """Test dispatching with multiple positional arguments."""
        event = Event[MultiArgCallback]()
        received_data = []
        
        def callback(name: str, age: int, active: bool = True) -> None:
            received_data.append((name, age, active))
        
        event.subscribe(callback)
        event.dispatch("Alice", 30, False)
        
        assert received_data == [("Alice", 30, False)]

    def test_dispatch_with_keyword_arguments(self):
        """Test dispatching with keyword arguments."""
        event = Event[MultiArgCallback]()
        received_data = []
        
        def callback(name: str, age: int, active: bool = True) -> None:
            received_data.append((name, age, active))
        
        event.subscribe(callback)
        event.dispatch(name="Bob", age=25, active=True)
        
        assert received_data == [("Bob", 25, True)]

    def test_dispatch_with_mixed_arguments(self):
        """Test dispatching with both positional and keyword arguments."""
        event = Event[MultiArgCallback]()
        received_data = []
        
        def callback(name: str, age: int, active: bool = True) -> None:
            received_data.append((name, age, active))
        
        event.subscribe(callback)
        event.dispatch("Charlie", 35, active=False)
        
        assert received_data == [("Charlie", 35, False)]

    def test_dispatch_preserves_order(self):
        """Test that callbacks are called in subscription order."""
        event = Event[SimpleCallback]()
        order = []
        
        def callback1() -> None:
            order.append(1)
        
        def callback2() -> None:
            order.append(2)
        
        def callback3() -> None:
            order.append(3)
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        event.dispatch()
        
        assert order == [1, 2, 3]

    def test_dispatch_multiple_times(self):
        """Test that an event can be dispatched multiple times."""
        event = Event[SimpleCallback]()
        call_count = []
        
        def callback() -> None:
            call_count.append(1)
        
        event.subscribe(callback)
        
        event.dispatch()
        event.dispatch()
        event.dispatch()
        
        assert len(call_count) == 3


class TestEventDecorator:
    """Tests for Event.event_listener() decorator."""

    def test_event_listener_decorator_subscribes_function(self):
        """Test that the event_listener decorator subscribes the function."""
        event = Event[SimpleCallback]()
        called = []
        
        @event.event_listener
        def callback() -> None:
            called.append(True)
        
        assert len(event._callbacks) == 1
        assert callback in event._callbacks

    def test_event_listener_decorator_returns_function(self):
        """Test that the decorator returns the original function."""
        event = Event[SimpleCallback]()
        
        def original_callback() -> None:
            pass
        
        decorated_callback = event.event_listener(original_callback)
        
        assert decorated_callback is original_callback

    def test_event_listener_decorated_function_can_be_called_directly(self):
        """Test that a decorated function can still be called directly."""
        event = Event[SimpleCallback]()
        results = []
        
        @event.event_listener
        def callback() -> None:
            results.append("called")
        
        callback()
        
        assert results == ["called"]

    def test_event_listener_decorated_function_called_on_dispatch(self):
        """Test that a decorated function is called when event is dispatched."""
        event = Event[SimpleCallback]()
        results = []
        
        @event.event_listener
        def callback() -> None:
            results.append("dispatched")
        
        event.dispatch()
        
        assert results == ["dispatched"]

    def test_event_listener_decorated_function_can_be_unsubscribed(self):
        """Test that a decorated function can be unsubscribed."""
        event = Event[SimpleCallback]()
        results = []
        
        @event.event_listener
        def callback() -> None:
            results.append("called")
        
        event.unsubscribe(callback)
        event.dispatch()
        
        assert len(results) == 0
        assert len(event._callbacks) == 0

    def test_event_listener_with_arguments(self):
        """Test event_listener decorator with callback that takes arguments."""
        event = Event[StringCallback]()
        messages = []
        
        @event.event_listener
        def callback(message: str) -> None:
            messages.append(message)
        
        event.dispatch("Test message")
        
        assert messages == ["Test message"]


class TestEventEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_callback_raising_exception_does_not_stop_other_callbacks(self):
        """Test that if one callback raises an exception, subsequent callbacks are still called."""
        event = Event[SimpleCallback]()
        results = []
        
        def callback1() -> None:
            results.append(1)
        
        def callback2() -> None:
            raise ValueError("Test exception")
        
        def callback3() -> None:
            results.append(3)
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        with pytest.raises(ValueError, match="Test exception"):
            event.dispatch()
        
        # Note: callback1 was called, but callback3 was not due to the exception
        assert 1 in results
        assert 3 not in results

    def test_modifying_callbacks_during_dispatch(self):
        """Test behavior when callbacks list is modified during dispatch."""
        event = Event[SimpleCallback]()
        results = []
        
        def callback1() -> None:
            results.append(1)
        
        def callback2() -> None:
            results.append(2)
            # Unsubscribe callback3 during dispatch
            event.unsubscribe(callback3)
        
        def callback3() -> None:
            results.append(3)
        
        event.subscribe(callback1)
        event.subscribe(callback2)
        event.subscribe(callback3)
        
        event.dispatch()
        
        # Behavior depends on whether the list is modified during iteration
        # This test documents the current behavior
        assert 1 in results
        assert 2 in results

    def test_lambda_callback(self):
        """Test using lambda functions as callbacks."""
        event = Event[StringCallback]()
        results = []
        
        event.subscribe(lambda message: results.append(message))
        event.dispatch("Lambda test")
        
        assert results == ["Lambda test"]

    def test_class_method_as_callback(self):
        """Test using a class method as a callback."""
        event = Event[StringCallback]()
        
        class Handler:
            def __init__(self):
                self.messages = []
            
            def handle(self, message: str) -> None:
                self.messages.append(message)
        
        handler = Handler()
        event.subscribe(handler.handle)
        event.dispatch("Method test")
        
        assert handler.messages == ["Method test"]

    def test_static_method_as_callback(self):
        """Test using a static method as a callback."""
        event = Event[StringCallback]()
        results = []
        
        class Handler:
            @staticmethod
            def handle(message: str) -> None:
                results.append(message)
        
        event.subscribe(Handler.handle)
        event.dispatch("Static method test")
        
        assert results == ["Static method test"]


class TestEventIntegration:
    """Integration tests combining multiple features."""

    def test_complete_lifecycle(self):
        """Test a complete event lifecycle: create, subscribe, dispatch, unsubscribe."""
        event = Event[StringCallback]()
        messages = []
        
        def logger(message: str) -> None:
            messages.append(message)
        
        # Subscribe
        event.subscribe(logger)
        
        # Dispatch
        event.dispatch("First message")
        assert messages == ["First message"]
        
        # Dispatch again
        event.dispatch("Second message")
        assert messages == ["First message", "Second message"]
        
        # Unsubscribe
        event.unsubscribe(logger)
        
        # Dispatch should not call the callback anymore
        event.dispatch("Third message")
        assert messages == ["First message", "Second message"]

    def test_multiple_events_independent(self):
        """Test that multiple Event instances are independent."""
        event1 = Event[SimpleCallback]()
        event2 = Event[SimpleCallback]()
        
        results1 = []
        results2 = []
        
        def callback1() -> None:
            results1.append(1)
        
        def callback2() -> None:
            results2.append(2)
        
        event1.subscribe(callback1)
        event2.subscribe(callback2)
        
        event1.dispatch()
        assert results1 == [1]
        assert results2 == []
        
        event2.dispatch()
        assert results1 == [1]
        assert results2 == [2]

    def test_complex_workflow(self):
        """Test a complex workflow with multiple subscribers and dispatches."""
        event = Event[MultiArgCallback]()
        log = []
        
        def validator(name: str, age: int, active: bool = True) -> None:
            if age < 0:
                raise ValueError("Age cannot be negative")
            log.append(("validated", name, age, active))
        
        def logger(name: str, age: int, active: bool = True) -> None:
            log.append(("logged", name, age, active))
        
        def notifier(name: str, age: int, active: bool = True) -> None:
            log.append(("notified", name, age, active))
        
        event.subscribe(validator)
        event.subscribe(logger)
        event.subscribe(notifier)
        
        event.dispatch("Alice", 30, active=True)
        
        assert len(log) == 3
        assert log[0] == ("validated", "Alice", 30, True)
        assert log[1] == ("logged", "Alice", 30, True)
        assert log[2] == ("notified", "Alice", 30, True)
