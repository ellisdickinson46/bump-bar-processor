import asyncio
import json
import re
import aiofiles


class JSONHandler:
    def __init__(self, json_file=None, encoding="utf-8"):
        self.file_name = json_file
        self.encoding = encoding
        self.json_data = self._run_sync(self._read_json())

    async def _read_json(self) -> dict[str, any]:
        try:
            async with aiofiles.open(self.file_name, "r", encoding=self.encoding) as json_file:
                data = await json_file.read()
                return json.loads(data)
        except FileNotFoundError as e:
            raise e
        except json.JSONDecodeError as e:
            raise e

    async def _write_json(self, data: dict[str, any]):
        try:
            async with aiofiles.open(self.file_name, "w", encoding=self.encoding) as json_file:
                await json_file.write(json.dumps(data, indent=4))
        except Exception as e:
            raise e

    def _run_sync(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            task = loop.create_task(coro)
            return loop.run_until_complete(task)

    def _resolve_keys(self, keys):
        if isinstance(keys, str):
            keys = keys.split('.')
        if not isinstance(keys, list):
            raise TypeError("Keys must be a string or a list.")
        return keys

    def get(self, keys, default=None):
        keys = self._resolve_keys(keys)
        data = self.json_data
        try:
            for key in keys:
                if not isinstance(data, dict):
                    return default
                data = data.get(key, default)
                if data is None:
                    return default
            return data
        except (KeyError, TypeError):
            return default

    def set(self, keys, value):
        """
        Update the in-memory JSON data of a specific key without writing to the file.
        
        Args:
            keys (str | list): Dot-separated string or list of keys representing the path.
            value (any): The value to set at the specified path.
        """
        keys = self._resolve_keys(keys)
        data = self.json_data
        try:
            for key in keys[:-1]:
                if key not in data or not isinstance(data[key], dict):
                    data[key] = {}
                data = data[key]
            data[keys[-1]] = value
        except (TypeError, KeyError) as e:
            raise ValueError(f"Invalid key path: {'.'.join(keys)}") from e

    def write(self):
        """
        Write the in-memory JSON data to the file.
        """
        self._run_sync(self._write_json(self.json_data))

    def revert(self):
        """
        Revert the in-memory data to the original state from the file on disk.
        """
        self.json_data = self._run_sync(self._read_json())
    
    def overwrite(self, new_data: dict):
        """
        Overwrite the entire JSON data with the new data.
        
        Args:
            new_data (dict): The new data to replace the existing JSON data.
        
        Raises:
            TypeError: If new_data is not a dictionary.
        """
        if not isinstance(new_data, dict):
            raise TypeError("New data must be a dictionary.")
        
        self.json_data = new_data


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class JSONValidator:
    def __init__(self, schema):
        self.schema = schema
        self.errors = []

    def _validate(self, value, schema, path="root"):
        if 'type' in schema:
            if schema['type'] == 'object':
                if not isinstance(value, dict):
                    self.errors.append(f"{path}: Expected object, got {type(value).__name__}")
                    return False
                
                # Check required fields
                required = schema.get('required', [])
                for key in required:
                    if key not in value:
                        self.errors.append(f"{path}: Missing required field '{key}'")
                
                # Check properties
                properties = schema.get('properties', {})
                for key, sub_schema in properties.items():
                    if key in value:
                        self._validate(value[key], sub_schema, path=f"{path}.{key}")

            elif schema['type'] == 'array':
                if not isinstance(value, list):
                    self.errors.append(f"{path}: Expected array, got {type(value).__name__}")
                    return False
                
                if 'minItems' in schema and len(value) < schema['minItems']:
                    self.errors.append(f"{path}: Array too short ({len(value)} items)")

                if 'maxItems' in schema and len(value) > schema['maxItems']:
                    self.errors.append(f"{path}: Array too long ({len(value)} items)")

                item_schema = schema.get('items')
                if item_schema:
                    for i, item in enumerate(value):
                        self._validate(item, item_schema, path=f"{path}[{i}]")

            elif schema['type'] == 'string':
                if not isinstance(value, str):
                    self.errors.append(f"{path}: Expected string, got {type(value).__name__}")
                
                if 'enum' in schema and value not in schema['enum']:
                    self.errors.append(f"{path}: Invalid enum value '{value}'")
                
                if 'pattern' in schema and not re.match(schema['pattern'], value):
                    self.errors.append(f"{path}: Invalid pattern for value '{value}'")

            elif schema['type'] == 'integer':
                if not isinstance(value, int):
                    self.errors.append(f"{path}: Expected integer, got {type(value).__name__}")

            elif schema['type'] == 'boolean':
                if not isinstance(value, bool):
                    self.errors.append(f"{path}: Expected boolean, got {type(value).__name__}")

            else:
                self.errors.append(f"{path}: Unsupported type '{schema['type']}'")

        return not bool(self.errors)
    
    def validate(self, data):
        self.errors = []  # Reset errors
        if not self._validate(data, self.schema):
            error_message = "\n".join(self.errors)
            raise ValidationError(f"Configuration Validation failed:\n{error_message}")
        return True