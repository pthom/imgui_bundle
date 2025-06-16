# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import Callable, TypeVar, Any
from munch import Munch  # type: ignore

# Create type variables for the argument and return types of the function
A = TypeVar("A", bound=Callable[..., Any])


def static(**kwargs: Any) -> Callable[[A], A]:
    """A decorator that adds static variables to a function
    :param kwargs: list of static variables to add
    :return: decorated function

    Example:
        @static(x=0, y=0)
        def my_function():
            # static vars are stored as attributes of "my_function"
            # we use static as a more readable synonym.
            static = my_function

            static.x += 1
            static.y += 2
            print(f"{static.f.x}, {static.f.x}")

        invoking f three times would print 1, 2 then 2, 4, then 3, 6

    Static variables are similar to global variables, with the same shortcomings!
    Use them only in small scripts, not in production code!
    """

    def decorator(func: A) -> A:
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorator


def run_anon_block(function: Callable[[], None]) -> None:
    """Decorator for anonymous block

    This enables you to emulate CC++ anonymous blocks.
    In the example below, _win_code() is an anonymous block which is evaluated right after its definition.
    Its presence makes it possible to indent parts of the code (for example, the code responsible for the widgets
     inside a window)

        imgui.begin("My window")
        @run_anon_block
        def _win_code():
            imgui.text("What is your name")
            changed_f, first_name = imgui.input_text("First name")
            changed_l, last_name = imgui.input_text("Last name")
            # ...
        imgui.end()

    """
    function()  # type: ignore


# Create type variables for the argument and return types of the function
AnyCallable = TypeVar("AnyCallable", bound=Callable[..., Any])


def add_static(func: AnyCallable) -> AnyCallable:
    """
    A decorator that adds a persistent 'static' attribute as a Munch object to a function.

    - The `static` attribute allows the function to store variables persistently across calls.
    - Unlike global variables, this keeps the state encapsulated within the function.
    - This is useful for maintaining UI state in ImGui-based applications.

    **Example:**
    ```python
    from imgui_bundle.immapp import add_static

    @add_static
    def counter_demo():
        static = counter_demo.static  # Access the static storage which was created by the decorator
                                      # You can add any attributes to this object.

        if not hasattr(static, "count"):
            static.count = 0  # Initialize on first run

        static.count += 1
        print(f"Counter: {static.count}")

    counter_demo()  # Output: Counter: 1
    counter_demo()  # Output: Counter: 2
    counter_demo()  # Output: Counter: 3
    ```

    **When to Use:**
    - Use `@add_static` when you need function-scoped persistent storage **without predefined values**.
    - You must manually initialize static variables inside the function.

    **Notes:**
    - This decorator is lightweight and adds no runtime overhead beyond attribute assignment.
    - It is especially useful in immediate mode GUI programming where state persistence is needed.
    - Static variables are similar to global variables, with the same shortcomings!
      Use them only in small scripts, not in production code!

    :param func: The function to decorate.
    :return: The decorated function with an attached `static` attribute.
    """

    if not hasattr(func, "static"):
        func.static = Munch()  # Initialize an empty storage container

    return func


def add_static_values(**defaults: Any) -> Callable[[A], A]:
    """
    A decorator that adds a persistent 'static' attribute as a Munch object with optional default values.

    - This is similar to `@add_static`, but allows you to define **default values** upfront.
    - The `static` attribute is created once and persists across function calls.
    - This is useful for initializing UI-related state variables without explicit checks.

    **Example:**
    ```python
    from imgui_bundle.immapp import add_static_values

    @add_static_values(count=0, step=2)
    def counter_demo():
        static = counter_demo.static  # Access the static storage which was created by the decorator
                                      # You can add any attributes to this object.

        static.count += static.step
        print(f"Counter: {static.count}")

    counter_demo()  # Output: Counter: 2
    counter_demo()  # Output: Counter: 4
    counter_demo()  # Output: Counter: 6
    ```

    **When to Use:**
    - Use `@add_static_values(default1=value1, default2=value2, ...)` **when you want pre-initialized static variables**.
    - No need for `if not hasattr(static, "var"):` checks inside the function.

    **Notes:**
    - This decorator is lightweight and only runs once per function definition.
    - Using `Munch`, it allows **dot-accessible** static variables (`static.var_name` instead of `static['var_name']`).
    - Static variables are similar to global variables, with the same shortcomings!
      Use them only in small scripts, not in production code!

    :param defaults: Keyword arguments representing the default static variables.
    :return: A decorator that adds a `static` attribute to the function.
    """

    def decorator(func: A) -> A:
        func.static = Munch(defaults)  # Initialize with user-defined defaults
        return func

    return decorator
