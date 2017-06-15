// Hook a Java class and init a global method available inside hook

// init the frida helper class
var h = FridaHelper();
// this will enable a global function called dump which allow show an hexdump of some data
helper.support_dump(true);
// this will hook the native method EVP_DecryptInit_ex inside libcrypto.so , using handleInit as callback
h.find_and_hook_native('libcrypto.so','EVP_DecryptInit_ex',handleInit);
// this is the callback method, this is called twice onenter and onexit , you can check whenever you're onenter or exit
// by checking the data parameter as following
function handleInit(data)
{
    // check if we are not onExit since is result will be true just onExit
	if(!data.is_result)
	{
	    // Dump the third parameter the key used to decrypt
		send("Key: " + dump(data.args[3], 32));
	}
}
// Attach frida to the following process
h.start('challenge.teamsik.aesdecryption');

