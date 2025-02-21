from dataclasses import dataclass
from typing import List, Dict

prompt = """You are given a user profile:{profile}. 
Here is some platforms:{platforms}. 
Here is some apis under the platforms:{tools}.
The user will give you a query. Based on the profile, try to solve the query by using the platforms and apis. The platform you choose should fit the user profile or the needs of the user's query. All the necessary information are provided in the user profile. DO NOT ask the user for further information. 
You should respond in the format of {format} No other text MUST be included."""

format = "platform:[func1(param1_name = param1_value, param2...), func2...]"
#format = "{'platform':platform_name, 'functions':[{'name':func1_name, 'parameters':{param1_name:param1_value, param2...}}, func2...]}"

TASK_INSTRUCTION = """You are given a user profile:{profile}. 
Here is some platforms:{platforms}. 
The user will give you a query. Based on the profile, try to solve the query by using the platforms and apis. The platform you choose should fit the user profile or the needs of the user's query. All the necessary information are provided in the user profile. DO NOT ask the user for further information. 
"""
FORMAT_INSTRUCTION = "You should respond in the format of {format} No other text MUST be included."



@dataclass
class Template:
    system_format: str ="{content}"
    user_format: str ="{content}"
    assistant_format: str ="{content}"
    formatting_format: str = None
    stop_words: List[str] = None

    def return_stop_words(self):
        return self.stop_words
    
    def return_prompt(self, profile, platforms, tools, query):
        return  self.system_format.format(content = prompt.format(profile = profile, platforms = platforms, tools = tools, format = format))+ self.user_format.format(content = query) + self.assistant_format

TEMPLATES: Dict[str, "Template"] = {}

def register_template(name, system_format, user_format, assistant_format, stop_words, return_prompt=None):
    TEMPLATES[name] = Template(system_format, user_format, assistant_format, stop_words)
    if return_prompt != None:
        TEMPLATES[name].return_prompt = return_prompt

def get_template(name):
    return TEMPLATES[name]


register_template(
    name = "qwen",
    system_format = "<|im_start|>system\n{content}<|im_end|>\n",
    user_format = "<|im_start|>user\n{content}<|im_end|>\n",
    assistant_format = "<|im_start|>assistant",
    stop_words = ["<|im_end|>"]
)


register_template(
    name = "llama3",
    system_format = "<|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>",
    user_format = "<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>",
    assistant_format = "<|start_header_id|>assistant<|end_header_id|>\n\n",
    stop_words = ["<|eot_id|>"]
)


register_template(
    name="mistral",
    system_format = "{content}\n\n",
    user_format = "[INST] {content}[/INST]",
    assistant_format = " ",
    stop_words = ["eos_token"]
)


def deepseek3_return_prompt(self, profile, platforms, tools, query, format):
    return self.system_format + self.user_format.format(content = prompt.format(profile = profile, platforms = platforms, tools = tools, format = format)) + query + self.assistant_format

register_template(
    name="deepseek3",
    system_format="<｜begin▁of▁sentence｜>",
    user_format="<｜User｜>{{content}}",
    assistant_format= "<｜Assistant｜><think>\n",
    stop_words=["<｜end▁of▁sentence｜>"],
    return_prompt=deepseek3_return_prompt
)


def hammer_return_prompt(self, profile, platforms, tools, query, format):
    content = f"[BEGIN OF TASK INSTRUCTION]\n{TASK_INSTRUCTION.format(profile=profile, platforms=platforms)}\n[END OF TASK INSTRUCTION]\n\n"
    content += f"[BEGIN OF AVAILABLE TOOLS]\n{tools}\n[END OF AVAILABLE TOOLS]\n\n"
    content += f"[BEGIN OF FORMAT INSTRUCTION]\n{FORMAT_INSTRUCTION.format(format=format)}\n[END OF FORMAT INSTRUCTION]\n\n"
    user_query = f"<|im_start|>user\n{query}<im_end>\n"
    return self.system_format + self.user_format.format(content=content) + user_query + self.assistant_format

register_template(
    name="hammer",
    system_format="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n",
    user_format="<|im_start|>user\n{content}<|im_end|>",
    assistant_format= "<|im_start|>assistant\n",
    stop_words=["<im_end>"],
    return_prompt=hammer_return_prompt
)


def xlam_return_prompt(self, profile, platforms, tools, query, format):
    content = f"[BEGIN OF AVAILABLE TOOLS]\n{tools}\n[END OF AVAILABLE TOOLS]\n\n"
    content += f"[BEGIN OF FORMAT INSTRUCTION]\n{FORMAT_INSTRUCTION.format(format=format)}\n[END OF FORMAT INSTRUCTION]\n\n"
    return self.system_format.format(content = TASK_INSTRUCTION.format(profile=profile, platforms=platforms)) + content + self.user_format.format(content=query) + self.assistant_format

register_template(
    name="xlam",
    system_format="[BEGIN OF TASK INSTRUCTION]\n{content}\n[END OF TASK INSTRUCTION]\n\n",
    user_format="[BEGIN OF QUERY]\n{content}\n[END OF QUERY]\n\n",
    assistant_format= "[BEGIN OF SOLUTION]\n",
    stop_words=["[END OF SOLUTION]"],
    return_prompt=xlam_return_prompt
)
