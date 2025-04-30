import io
import json
import logging
from typing import Any, Dict, Optional, Type, get_args, get_origin

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def format_json_result(
    json_data,
    model: Optional[Type[BaseModel]] = None,
    prompt_append: Optional[str] = None,
    csv: Optional[bool] = True,
) -> Any:
    """
    Safely extract and format the 'result' field from JSON data.

    - If 'json_data' is not a dict or lacks 'result', returns it directly.
    - If 'result' is a primitive (bool, int, float, None), returns it directly.
    - If 'result' is a str, tries to parse it as JSON; on failure, returns original json_data.
    - If 'result' is a dict or list of dicts, converts to a CSV string with optional field descriptions.
    - Any unexpected errors cause returning the original json_data.

    :param json_data: JSON data (string or dict)
    :param descriptions: Pydantic BaseModel class for field descriptions (must define a 'result' field)
    :param reason: Optional reason metadata
    :return: Primitive, original json_data, or dict containing CSV data and metadata
    """
    try:
        if csv is False:
            return {
                "_prompt_append": prompt_append,
                "data": {
                    "type": "json",
                    "description": get_field_descriptions(model) if model else {},
                    "value": json_data,
                },
            }

        # Load JSON string input
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                return json_data

        # Must be a dict with 'result'
        if not isinstance(json_data, dict) or "result" not in json_data:
            return json_data

        result = json_data["result"]

        # Return primitives immediately
        if isinstance(result, (bool, int, float, type(None))):
            return result

        # If string, try parsing
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                return json_data

        # Only dict or list of dict
        if isinstance(result, dict):
            items = [result]
        elif isinstance(result, list) and all(isinstance(i, dict) for i in result):
            items = result
        else:
            return json_data

        # Determine CSV columns
        keys = set()
        for item in items:
            keys.update(item.keys())
        keys = ["number"] + sorted(keys - {"number"})

        def serialize_value(value: Any) -> Any:
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return value

        # Build CSV String
        csv_io = io.StringIO()
        writer = csv.DictWriter(csv_io, fieldnames=keys)
        writer.writeheader()

        for idx, itm in enumerate(items, start=1):
            row = {"number": idx}
            for k in keys:
                if k != "number":
                    row[k] = serialize_value(itm.get(k))
            writer.writerow(row)
        csv_str = csv_io.getvalue()
        csv_io.close()

        return {
            "_prompt_append": prompt_append,
            "data": {
                "type": "csv",
                "description": get_field_descriptions(model) if model else {},
                "value": csv_str,
            },
        }
    except Exception as e:
        logger.error(f"Error: {e}")  # For debugging
        return json_data


def get_field_descriptions(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Recursively extract field descriptions from a Pydantic model and its nested models.

    Args:
        model: A Pydantic BaseModel class

    Returns:
        Dictionary with field names as keys and descriptions (or nested description objects) as values
    """
    descriptions = {}

    # Check if it's actually a model
    if not hasattr(model, "model_fields"):
        return descriptions

    for field_name, field_info in model.model_fields.items():
        # Get the base description
        field_description = field_info.description

        # Get the actual type, handling Optional, List, etc.
        field_type = field_info.annotation
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Handle List[SomeModel] or Optional[SomeModel] cases
        nested_type = None
        if origin is not None and args:
            # For List[Model], Union[Model, None], etc.
            for arg in args:
                if hasattr(arg, "model_fields"):
                    nested_type = arg
                    break
        elif hasattr(field_type, "model_fields"):
            # Direct model field
            nested_type = field_type

        if nested_type:
            # It's a nested model, so get its subfields recursively
            subfields = get_field_descriptions(nested_type)
            descriptions[field_name] = {
                "description": field_description,
                "subfields": subfields,
            }
        else:
            # Regular field, just store the description
            descriptions[field_name] = field_description

    return descriptions
