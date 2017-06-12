// Hook a Java class and print hello world when triggered

// init the frida helper class
helper = FridaHelper();
// find and hook a specified method of a class, remember a process name must , and an hook function must be specified
helper.find_and_hook_method("com.android.vending", "java.lang.String", "equals", equalsHookFunction)
// com.android.vending is the process to attach to
// java.lang.String is our selected class
// equals is the method to hook , you don't have to worry about overloads everyone is hooked at once
// equalsHookFunction is where we land once equals is called

// Define a land function equalsHookFunction, it must accept a "data" parameters, here you will receive every info
// regarding caller class such as (overload name, parameters types and value and much more)
// remember every hook function is called twice on enter and on exit, so you will see Hello World two times!
// also remember than there is an high level of separation between the function hook equalsHookFunction and the
// global scope so without an addition trick equalsHookFunction can't access the global objects declared above!
function equalsHookFunction(data)
{
    send("Hello World!");
}
// Start the actual hooking process, com.android.vending is the process we want to hook
helper.start("com.android.vending");

