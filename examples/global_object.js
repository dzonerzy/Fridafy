// Hook a Java class and init a global method available inside hook

// init the frida helper class
helper = FridaHelper();
// find and hook a specified method of a class, remember a process name must , and an hook function must be specified
helper.find_and_hook_method("com.android.vending", "java.lang.String", "equals", equalsHookFunction)
// com.android.vending is the process to attach to
// java.lang.String is our selected class
// equals is the method to hook , you don't have to worry about overloads everyone is hooked at once
// equalsHookFunction is where we land once equals is called

// Sometimes we may need to use a previous declare object inside out function hook ,this is possible via
// create_global api ad following
// helper.create_global("variableName", object)
helper.create_global("sayHello", funcSayHello);
function sayHello(name)
{
    send("Hello! "+name);
}
// Create a global array
helper.create_global("myArray", new Array(0,1,2));
// Define a land function equalsHookFunction, it must accept a "data" parameters, here you will receive every info
// regarding caller class such as (overload name, parameters types and value and much more)
// remember every hook function is called twice on enter and on exit, so you will see Hello World two times!
function equalsHookFunction(data)
{
    // using create_global api we have defined a global variable with our function sayHello!
    sayHello("Frida");
    // show an element from array
    send("2 == " + myArray[2]);
}
