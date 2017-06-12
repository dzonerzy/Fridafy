// Hook a Java class and print an hexdump when triggered

// init the frida helper class
helper = FridaHelper();
// find and hook a specified method of a class, remember a process name must , and an hook function must be specified
helper.find_and_hook_method("com.android.vending", "java.lang.String", "equals", equalsHookFunction)
// com.android.vending is the process to attach to
// java.lang.String is our selected class
// equals is the method to hook , you don't have to worry about overloads everyone is hooked at once
// equalsHookFunction is where we land once equals is called

// this will enable a global function called hexdump which allow show an hexdump of some data
helper.support_callstack(true);

// this will enable a global function called bin2str which allow to convert an array of byte to a string
helper.support_bin2str(true);

// Define a land function equalsHookFunction, it must accept a "data" parameters, here you will receive every info
// regarding caller class such as (overload name, parameters types and value and much more)
// remember every hook function is called twice on enter and on exit, so you will see Hello World two times!
function equalsHookFunction(data)
{
    // in order to retrieve whenever we are on enter or exit we can use the data object like following
    if(data.is_result)
    {
        send("On Exit!");
        // Sometimes functions return something we can retrieve the return object by checking data.result
        // in our case this may return true or false
        send("Result: " + data.result);
    }else{
        send("On Enter!");
        // Other times we may want to get the parameters passed to a function, these are stored on data.params
        // data.params is an array of dictionary composed by type => param type and value => param value
        // let's print them out!
        for(var i=0; i<data.params.length; i++)
        {
            // print out type
            send("type => " + data.params[i].type);
            // print out value (toString)
            // let's assume that our input is an array , and let's show an hexdump
            send("value => \n" + bin2str(hexdump(data.params[i].value)));
        }
    }
}
// Start the actual hooking process, com.android.vending is the process we want to hook
helper.start("com.android.vending");
