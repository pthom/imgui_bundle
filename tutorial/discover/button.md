# Handling button events

We will now create an application which handles clicks on a button, and updates a counter each time the button is clicked:

![](button.jpg)

We will follow the steps below:
1. Add an AppState class to store the state of the application. This is a recommended best practice, as it allows to separate the GUI code from the business logic.
2. Add a counter to the AppState. This counter will be incremented each time a button is clicked.
3. Let the gui function take an AppState as an argument (and possibly modify it).
4. Add a button to the GUI, with `imgui.button()`, and increment the counter when the button is clicked.
5. Add a tooltip to the button, to display a message when the user hovers over it.
6. Add a button to exit the application (see note below).
7. Create a main() function to run the application, where we create an AppState object
8. Create a lambda function to call the gui function with the AppState object as an argument.
9. Call `hello_imgui.run()` with the lambda function as an argument.

*Note: In the case of a web application, such as in this tutorial, the "exit" button will not have any effect. In the case of a desktop application, it will close the window.*


**Python**
```{literalinclude} button.py
```


**C++**
```{literalinclude} button.cpp
```
