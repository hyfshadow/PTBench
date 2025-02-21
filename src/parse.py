import json
import ast
import re

def ast_parse(input_str):
    return ast_parse_1(input_str)

def ast_parse_1(input_str):
    input_str = '{'+input_str+'}'
    parsed = ast.parse(input_str, mode="eval")
    extracted = []
    if isinstance(parsed.body.keys[0], ast.Name):
        key = parsed.body.keys[0].id
    elif isinstance(parsed.body.keys[0], ast.Constant):
        key = parsed.body.keys[0].value
    body = parsed.body.values[0]
    if isinstance(body, ast.Call):
        extracted.append(resolve_ast_call(body))
    else:
        for elem in body.elts:
            assert isinstance(elem, ast.Call)
            extracted.append(resolve_ast_call(elem))
    return (key, extracted)


def resolve_ast_call(elem):
    # Handle nested attributes for deeply nested module paths
    func_parts = []
    func_part = elem.func
    while isinstance(func_part, ast.Attribute):
        func_parts.append(func_part.attr)
        func_part = func_part.value
    if isinstance(func_part, ast.Name):
        func_parts.append(func_part.id)
    func_name = ".".join(reversed(func_parts))
    args_dict = {}
    for arg in elem.keywords:
        output = resolve_ast_by_type(arg.value)
        args_dict[arg.arg] = output
    return {func_name: args_dict}


def resolve_ast_by_type(value):
    if isinstance(value, ast.Constant):
        if value.value is Ellipsis:
            output = "..."
        else:
            output = value.value
    elif isinstance(value, ast.UnaryOp):
        output = -value.operand.value
    elif isinstance(value, ast.List):
        output = [resolve_ast_by_type(v) for v in value.elts]
    elif isinstance(value, ast.Dict):
        output = {
            resolve_ast_by_type(k): resolve_ast_by_type(v)
            for k, v in zip(value.keys, value.values)
        }
    elif isinstance(
        value, ast.NameConstant
    ):  # Added this condition to handle boolean values
        output = value.value
    elif isinstance(
        value, ast.BinOp
    ):  # Added this condition to handle function calls as asrguments
        output = eval(ast.unparse(value))
    elif isinstance(value, ast.Name):
        output = value.id
    elif isinstance(value, ast.Call):
        if len(value.keywords) == 0:
            output = ast.unparse(value)
        else:
            output = resolve_ast_call(value)
    elif isinstance(value, ast.Tuple):
        output = tuple(resolve_ast_by_type(v) for v in value.elts)
    elif isinstance(value, ast.Lambda):
        output = eval(ast.unparse(value.body[0].value))
    elif isinstance(value, ast.Ellipsis):
        output = "..."
    elif isinstance(value, ast.Subscript):
        try:
            output = ast.unparse(value.body[0].value)
        except:
            output = ast.unparse(value.value) + "[" + ast.unparse(value.slice) + "]"
    else:
        raise Exception(f"Unsupported AST type: {type(value)}")
    return output

def ast_parse_2(answer):
    #answer = answer[answer.find('</think>'):]
    answer = json.loads(answer.replace("'",'"').replace('True','true').replace('False','false'))
    platform = answer["platform"]
    funcs = answer["functions"]
    funcs_new = []
    for func in funcs:
        func_new = {}
        func_new[func["name"]] = func["parameters"]
        funcs_new.append(func_new)
    return platform, funcs_new