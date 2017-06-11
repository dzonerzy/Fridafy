// Hook a Java class and show how to check for triggered overload + filtering

// init the frida helper class
helper = FridaHelper();
// find and hook a specified method of a class, remember a process name must , and an hook function must be specified
helper.find_and_hook_method("com.android.vending", "javax.crypto.Cipher", "doFinal", doFinalHookFunction)
// com.android.vending is the process to attach to
// java.lang.String is our selected class
// equals is the method to hook , you don't have to worry about overloads everyone is hooked at once
// equalsHookFunction is where we land once equals is called

// Define a land function equalsHookFunction, it must accept a "data" parameters, here you will receive every info
// regarding caller class such as (overload name, parameters types and value and much more)
// remember every hook function is called twice on enter and on exit, so you will see Hello World two times!

function doFinalHookFunction(data)
{
    // Some method may one on or more overload (method with same name but different params, so how we can understand
    // which one was called? easy data.signature will contains a string which describe the current called function
    send("We are inside => " + data.signature)
    // otherwise you can just count number of parameters
    // if(data.params.length == 5) { ..... just activate when the called function have 5 params
    // otherwise you can check the parameters type
    // if(data.params[0].type == "java.lang.String") { .... then do something
}
