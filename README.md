# Bump Bar Processor

A modular Python tool for listening to serial input from Bump Bars  
_Tested with: Panasonic JS140MS, TG3 KBA-FP10A_


## 📦 Features

- ✅ Serial port listener with auto-reconnect
- 🔌 Plugin-based command execution
- ⚙️ JSON-based configuration
- 🧪 Hardware test mode
- 📜 Cross-platform serial port detection

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare configuration

Example `config.json`:

```json
{
  "commands": {
    "e1": {
      "plugin": "plugins.platform_command",
      "kwargs": {
        "command": "echo 'Hello from Terminal'"
      }
    },
    "e2": {
      "plugin": "plugins.hello_world"
    }
  },
  "connection": {
    "baud": 1200,
    "port": "/dev/tty.PL2303G-USBtoUART130"
  },
  "feature_flags": {
    "enable_repeat_presses": true,
    "enable_auto_reconnect": false
  }
}
```

---

## 📚 Usage

### List available serial ports

```bash
python main.py list-ports
```

### Run with config file

```bash
python main.py run config.json
```

### Hardware test mode (manual arguments)

```bash
python main.py hw-test -b 9600 -p COM3 -a -r
```

> `-b`: Set Baud Rate (defaults to 1200)  
> `-p`: Set Port Name/Path  
> `-a`: Enable auto-reconnect  
> `-r`: Enable repeat key presses  

## 🔌 Plugin System

Plugins are Python scripts with a `run(logger, **kwargs)` function.

### Example: `plugins/platform_command.py`

```python
def run(logger, **kwargs):
    command = kwargs.get("command")
    logger.info(f"Running: {command}")
    subprocess.run(command, shell=True)
```
