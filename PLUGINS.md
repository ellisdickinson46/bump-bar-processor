# Plugin Configuration

### Test Plugin
Log a test message to the console output.  
File: `plugins/hello_world.py`
```json
"a1": {
    "plugin": "plugins.hello_world"
}
```

### Web Requests
Send a web request (such as a webhook) to a specified address.  
File: `plugins/web_request.py`
```json
"a1": {
    "plugin": "plugins.web_request",
    "kwargs": {
        "method": "<<request_method>>",
        "url": "<<destination url>>"
    }
}
```

### Platform Commands
Run a console command as a subprocess (platform dependent)  
File: `plugins/platform_command.py`
```json
"a1": {
    "plugin": "plugins.platform_command",
    "kwargs": {
        "command": "<<console command>>"
    }
}
```
