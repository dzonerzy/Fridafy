"""
MIT License

Copyright (c) 2017 Daniele Linguaglossa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pyv8._PyV8 import JSFunction
from threading import Thread
from pyv8.PyV8 import *
import argparse
import frida
import time
import sys
import re

__all__ = ["version", "FridafyEngine"]

version = "0.1"

class Injector(object):
    def __init__(self, process=None, script=None, message_callback=None):
        self.process = process
        self.script = script
        self.message_callback = message_callback
        self.frida_process = None
        self.frida_script = None
        self.running = True

    def on_message(self, message, data):
        if callable(self.message_callback):
            return self.message_callback(message, data)
        else:
            if message['type'] == 'send':
                if type(message['payload']) not in [dict, list, int, float, bool, type(None)]:
                    print("[*] {0}".format(message['payload'].encode('utf-8')))
                else:
                    print("[*] {0}".format(message['payload']))
            else:
                print("[FridaError] {0}".format(message["description"].encode("utf-8")))

    def set_script(self, script):
        self.script = script

    def set_process(self, process):
        self.process = process

    def set_message_callback(self, message_callback):
        self.message_callback = message_callback

    def get_script(self):
        return self.script

    def attach(self):
        if self.process:
            attached = False
            while not attached:
                try:
                    process = frida.get_usb_device().attach(self.process)
                    self.frida_process = process
                    return
                except Exception:
                    pass
        else:
            print("[-] Error a process must be specified!")

    def stop(self):
        self.running = False

    def start(self):
        t = Thread(target=self._init_hook, args=())
        t.setDaemon(True)
        t.start()

    def _init_hook(self):
        self.attach()
        try:
            self.frida_script = self.frida_process.create_script(self.get_script())
            self.frida_script.on('message', self.on_message)
            self.frida_script.load()
        except frida.InvalidArgumentError as e:
            message = e.args[0]
            line = re.compile('Script\(line (\d+)\)')
            line = int(line.findall(message)[0])
            script = self.get_script().split("\n")
            if line > 0 and line - len(script)-1:
                lines = script[line-1] + "\n" "=> {0}".format(script[line]) + "\n" + script[line+1]
            else:
                lines = "=> {0}".format(script[line])
            print "[-] Error on line {0}:\n{1}: \n\n{2}".format(line, line, lines)
        except Exception as e:
            print("[-] Something weird happened during initialization: {0}".format(e))
        while self.running:
            try:
                pass
            except KeyboardInterrupt:
                self.running = False

class FridaHelper(JSClass):
    injector = Injector()
    overloads = []
    script_overloads = """
Java.perform(function() {
var className = Java.use('%s');
var x = className.%s.overload('int','int','int','int','int','int','int','int','int','int','int','int','int','int');
});
    """
    overload_re = re.compile('\((.*)\)')
    script_base = """
Java.perform(function() {{
send("Proudly powered by Fridafy v{0}");
%s
}});
    """.format(version)
    class_index = 1
    hooks = []
    has_class_created= False
    class_created = ""
    has_object_created = False
    object_created = ""
    has_hexdump_support = False
    hexdump_support = """
function hexdump(buffer)
{
    blockSize = 16;
    var lines = [];
    var hex = "0123456789ABCDEF";
    for (var b = 0; b < buffer.length; b += blockSize) {
        var block = buffer.slice(b, Math.min(b + blockSize, buffer.length));
        var addr = ("0000" + b.toString(16)).slice(-4);
        var codes = block.split('').map(function (ch) {
                var code = ch.charCodeAt(0);
                return " " + hex[(0xF0 & code) >> 4] + hex[0x0F & code];
        }).join("");
        codes += "   ".repeat(blockSize - block.length);
        var chars = block.replace(/[\\x00-\\x1F\\x20]/g, '.');
        chars +=  " ".repeat(blockSize - block.length);
        lines.push(addr + " " + codes + "  " + chars);
    }
    return "\\n"+lines.join("\\n");
}
    """
    has_callstack_support = False
    callstack_support = """
function callstack(shouldPrint)
{
    var trace = [];
    var stack = ThreadObj.currentThread().getStackTrace();
    if(shouldPrint)
    {
        send("------------------------------ Call Stack ---------------------------------");
        for(var i=0; i<stack.length; i++)
        {
                send(i + " => " + stack[i].toString());
        }
        send("--------------------------------------------------------------------------");
    }else{
        for(var i=0; i<stack.length; i++)
        {
               trace.push(stack[i].toString());
        }
        return trace;
    }
}
    """
    has_bin2str_support = False
    bin2str_support = """
function bin2str(array) {
    var result = "";
    for (var i = 0; i < array.length; i++) {
        result += String.fromCharCode(modulus(array[i], 256));
    }
    return result;
}

function modulus(x, n)
{

        return ((x%n)+n)%n;
}
    """

    @property
    def CLASS_CONSTRUCTOR(self):
        return "$init"

    def _on_message_overloads(self, message, data):
        if message['type'] == 'send':
            if type(message['payload']) not in [dict, list, int, float, bool, type(None)]:
                    print("[*] {0}".format(message['payload'].encode('utf-8')))
            else:
                    print("[*] {0}".format(message['payload']))
        else:
            if "does not match any of" in message["description"]:
                self.overloads = message["description"].split("\n\t")[1:]
            else:
                print("[-] {0}".format(message["description"].encode("utf-8")))

    def find_overloads(self, process_name, class_name, method_name):
        self.injector.set_script(self.script_overloads % (class_name, method_name))
        self.injector.set_process(process_name)
        self.injector.set_message_callback(self._on_message_overloads)
        self.injector.start()
        while not len(self.overloads) > 0:
            pass
        self.injector.stop()
        overloads = self.overloads
        self.overloads = []
        return overloads

    def _fake_parameters_type(self, overload):
        parameters = self.overload_re.findall(overload)[0]
        if len(parameters) > 1:
            overload_prams = parameters.strip()
            return overload_prams.replace("'", "")
        else:
            return ""

    def _fake_parameters(self, overload):
        params = []
        param_index = 1
        parameters = self.overload_re.findall(overload)[0]
        if len(parameters) > 1:
            overload_prams = parameters.strip().split(",")
            for _ in overload_prams:
                params.append("param{0}".format(param_index))
                param_index += 1
            return params
        else:
            return params

    def create_global(self, variable_name, obj):
        representation = {
            int: lambda x: x,
            float: lambda x: x,
            bool: lambda x: x,
            type(None): lambda x: x,
            unicode: lambda x: x.encode("utf-8"),
            JSArray: lambda x: "new Array()",
            JSFunction: lambda x: str(x),
        }
        self.has_object_created = True
        self.object_created += """
try
{
    var %s = %s;
}catch(e){
    send(e.toString());
}

        """ % (variable_name, representation[type(obj)](obj))

    def create_global_class(self, variable_name, class_name):
        self.has_class_created = True
        self.class_created += """
try
{
    var %s = Java.use('%s').$new();
}catch(e){
    send(e.toString());
}

        """ % (variable_name, class_name)

    def support_bin2str(self, flag):
        self.has_bin2str_support = flag

    def support_hexdump(self, flag):
        self.has_hexdump_support = flag

    def support_callstack(self, flag):
        if flag:
            self.create_global_class("ThreadObj", "java.lang.Thread")
        self.has_callstack_support = flag

    def find_and_hook_method(self, process_name, class_name, method, callback):
        hook_string = ""
        method_index = 1
        hook_string += "var class{0} = Java.use('{1}');\n".format(self.class_index, class_name)
        overloads = self.find_overloads(process_name, class_name, method)
        for overload in overloads:
            params = self._fake_parameters(overload)
            params_type = self._fake_parameters_type(overload)
            signature = "{0}.{1}({2})".format(class_name, method, params_type)
            hook_string += "var class{0}_method{1} = class{2}.{3}{4};\n\n".format(self.class_index, method_index,
                                                                                self.class_index, method, overload)
            hook_string += "class%s_method%s.implementation = function(%s){\n" % (self.class_index, method_index,
                                                                                  ",".join(params))
            callback_params = []
            if params_type:
                params_type = params_type.split(",")
            params_type = [x.strip() for x in params_type]
            for i in range(0, len(params)):
                if len(params):
                    callback_params.append('{"type": "%s", "value": %s}' % (params_type[i], params[i]))
            callback_data = '{"signature": "%s", "params": [%s], "is_result": false, "result": ""};\n' % (signature,
                                                                                            ",".join(callback_params))
            hook_string += "var signature = {0}".format(callback_data)
            hook_string += "{0}(signature);\n".format(callback.name)
            hook_string += "var ret = class%s_method%s.call(this%s);\n" % (self.class_index, method_index,
                                                                             "," +",".join(params)
                                                                             if len(params) > 0 else "")
            hook_string += "signature[\"is_result\"] = true;\n"
            hook_string += "signature[\"result\"] = ret;\n"
            hook_string += "{0}(signature);\n".format(callback.name)
            hook_string += "return ret;\n}\n"
            method_index += 1
        hook_string += str(callback) + "\n"
        self.class_index += 1
        self.hooks.append(hook_string)

    def start(self, process_name):
        full_script = ""
        if self.has_class_created:
            full_script += self.class_created + "\n"
        if self.has_object_created:
            full_script += self.object_created + "\n"
        if self.has_hexdump_support:
            full_script += self.hexdump_support + "\n"
        if self.has_callstack_support:
            full_script += self.callstack_support + "\n"
        if self.has_bin2str_support:
            full_script += self.bin2str_support + "\n"
        full_script += "".join(self.hooks)
        script = self.script_base % (full_script)
        self.injector.set_script(script)
        self.injector.set_process(process_name)
        self.injector.start()

class Global():
    def FridaHelper(self):
        return FridaHelper()

    def sleep(self, milliseconds):
        time.sleep(milliseconds/1000)

    def send(self, text):
        print("[*] {0}".format(text))

    def callstack(self, *args):
        pass

    def hexdump(self, *args):
        pass

    def bin2str(self, *args):
        pass

class FridafyEngine(object):
    def __init__(self):
        self.message_callback = None
        self.cursor = "[JS]> "
        self.use_previous = False
        self.global_script = ""

    def set_message_callback(self, callback):
        if callable(callback):
            self.message_callback = callback

    def execute(self, script):
        with JSContext(Global()) as ctx:
            try:
                ctx.eval(script)
            except JSError as e:
                if self.message_callback:
                    self.message_callback({"type": "error", "description": str(e)})
                else:
                    print("{0}: {1}".format(e.name, e.message))

    def interact(self):
         with JSContext(Global()) as ctx:
             while True:
                 try:
                    script = raw_input(self.cursor)
                    try:
                        if self.use_previous:
                            res = ctx.eval(self.global_script + script)
                        else:
                            res = ctx.eval(script)
                        if res is not None:
                            print str(res).encode('utf-8')
                        else:
                            if script:
                                print "undefined"
                        self.use_previous = False
                        self.cursor = "[JS]> "
                    except Exception as e:
                        if e.message == "Unexpected end of input":
                            self.global_script += script
                            self.cursor = "... "
                            self.use_previous = True
                        else:
                            self.use_previous = False
                            self.global_script = ""
                            print "{0}: {1}".format(e.name, e.message)
                 except KeyboardInterrupt:
                     print
                 except EOFError:
                     break

def main():
    parser = argparse.ArgumentParser(description="Fridafy Engine")
    parser.add_argument("-s", metavar="script", help="Script to run", required=False, dest="script")
    args = parser.parse_args()
    if args.script:
        script = ""
        try:
            with open(args.script, "r") as script_file:
                script = script_file.read()
                script_file.close()
        except IOError:
            print("Error: Unable to find script file")

        def on_message(data):
            if data["type"] == "error":
                print(data["description"])
                exit(0)
        if(script):
            engine = FridafyEngine()
            engine.set_message_callback(on_message)
            print("[*] Waiting for application...")
            engine.execute(script)
            try:
                raw_input()
            except (KeyboardInterrupt, EOFError):
                print("[-] Exiting...")
    else:
        print("[*] Launching FridaEngine interactive console - press CTRL+D to exit\n")
        engine = FridafyEngine()
        engine.interact()

if __name__ == "__main__":
    main()


