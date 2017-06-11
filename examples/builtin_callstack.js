// This example show how to setup some prebuilt functions useful during hooking

// init our helper
helper = FridaHelper();
// this will enable a global function called callstack which allow to retrieve or show a call stack frame during execution
helper.support_callstack(true);
// find and hook a specified method of a class, remember a process name must , and an hook function must be specified
helper.find_and_hook_method("com.android.vending", "java.lang.String", "equals", equalsHookFunction)
// com.android.vending is the process to attach to
// java.lang.String is our selected class
// equals is the method to hook , you don't have to worry about overloads everyone is hooked at once
// equalsHookFunction is where we land once equals is called

// Define a land function equalsHookFunction, it must accept a "data" parameters, here you will receive every info
// regarding caller class such as (overload name, parameters types and value and much more
function equalsHookFunction(data)
{
    // Show where equals was called by displaying call stack, it accept a parameter called shouldPrint, when set to
    // true callstack will print the callstack on video otherwise will return a string array
    callstack(true);
    // print just last element of call stack
    var stackArray = callstack(false);
    send(stackArray[stackArray.length-1]);
}