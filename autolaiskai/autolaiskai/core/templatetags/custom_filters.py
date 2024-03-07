from django import template
import ast

register = template.Library()

@register.filter
def extract_brackets_quotes(value):
   if isinstance(value, str):
        try:
            value_list = ast.literal_eval(value)
            if isinstance(value_list, list):
                # Join list items into a single string and strip whitespace and single quotes
                return ', '.join(str(item).strip("' ") for item in value_list)
        except (ValueError, SyntaxError):
            return value.strip("[]'\" ")
   elif isinstance(value, list):
        return ', '.join(str(item).strip("' ") for item in value)
   else:
        return value
   
@register.filter
def join_list_with_semicolon(input_list):
    real_list = ast.literal_eval(input_list)
    string_list = [str(item) for item in real_list]
    return '; '.join(string_list)