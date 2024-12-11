# Bump Bar Processor

A small bump bar script to connect and interpret inputs from Serial Bump Bars.

Tested with Panasonic and TG3 10-key Bump Bars  

## Configuration
Configuration is done through a single YAML file. Some values are platform dependent and use the native operating system interpreter.

A sample file is available.
### <code>connection</code> Keys
| Key       | Description              | Example Value                 | Type   |
|-----------|--------------------------|-------------------------------|--------|
| baud      | Serial Baud Rate         | 1200                          | String |
| port_name | Serial Port Name or Path | /dev/tty.PL2303G-USBtoUART140 | String |

### <code>button_commands</code> Keys
| Key       | Description                                      | Example Value | Type             |
|-----------|--------------------------------------------------|---------------|------------------|
| button_a2 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_a1 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_b1 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_b2 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_c1 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_c2 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_d1 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_d2 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_e1 | Command to execute (using native OS interpreter) | null          | String or _null_ |
| button_e2 | Command to execute (using native OS interpreter) | null          | String or _null_ |

### General Keys
| Key            | Description                                                     | Example Value | Type    |
|----------------|-----------------------------------------------------------------|---------------|---------|
| repeat_presses | Enable holding buttons for repeat actions                       | <true\|false> | Boolean |
| auto_reconnect | Enable reconnect attempts when bump bar connection is lost      | <true\|false> | Boolean |
| max_reconnects | Number of times to attempt reconnecting (use zero for infinite) | 0             | Integer |
