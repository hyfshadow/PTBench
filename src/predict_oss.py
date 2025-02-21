from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
import json
import os
from .template import get_template

def predict_oss(**kwargs):

    output_dir = kwargs["output_dir"]
    template_name = kwargs["template"]
    adapter_name_or_path = kwargs["adapter_name_or_path"]
    model_name_or_path = kwargs["model_name_or_path"]
    gpu_memory_utilization = kwargs["gpu_memory_utilization"]

    test_dir = kwargs["test_dir"]

    if adapter_name_or_path is not None:
        lora_request = LoRARequest("default", 1, adapter_name_or_path)
    else:
        lora_request = None
        
    llm = LLM(model=model_name_or_path, gpu_memory_utilization=gpu_memory_utilization, enable_lora=(adapter_name_or_path is not None))


    with open(test_dir+"/data.json", "r") as f:
        dataset = json.load(f)

    template = get_template(template_name)
    prompts = [template.return_prompt(
        profile = data["user_profile"], platforms = data["platforms"], tools = data["tools"], query = data["query"])
        for data in dataset]
    
    stop_words = template.return_stop_words()

    sampling_params = SamplingParams(temperature=0.1,stop=stop_words,max_tokens=128)
    # We turn on tqdm progress bar to verify it's indeed running batch inference
    outputs = llm.generate(prompts,
                        sampling_params=sampling_params,
                        lora_request=lora_request)

    if not os.path.exists(output_dir+'/'+test_dir):
        os.makedirs(output_dir+'/'+test_dir)

    with open(output_dir+'/'+test_dir+"/generation.jsonl", "w") as f:
        for output, data in zip(outputs, dataset):
            json.dump({"query":data["query"], "label":data["answer"], "predict":output.outputs[0].text}, f)
            f.write('\n')