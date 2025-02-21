from openai import OpenAI
import os
import httpx
import json
import tqdm

prompt = """You are given a user profile:{profile}. 
Here is some platforms:{platforms}. 
Here is some apis under the platforms:{tools}.
The user will give you a query. Based on the profile, try to solve the query by using the platforms and apis. The platform you choose should fit the user profile or the needs of the user's query. All the necessary information are provided in the user profile. DO NOT ask the user for further information. 
You should respond in the format of {format} No other text MUST be included."""

format = "platform:[func1(param1_name = param1_value, param2...), func2...]"

def predict_api(**kwargs):

    output_dir = kwargs["output_dir"]
    os.environ["OPENAI_API_KEY"] = kwargs["OPENAI_API_KEY"]
    os.environ["OPENAI_BASE_URL"] = kwargs["OPENAI_BASE_URL"]

    test_dir = kwargs["test_dir"]

    if not os.path.exists(output_dir+'/'+test_dir):
        os.makedirs(output_dir+'/'+test_dir)
        
    httpx_client = httpx.Client(verify=False)
    client = OpenAI(http_client=httpx_client)

    with open(test_dir+"/data.json", "r") as f:
        dataset = json.load(f)

    for data in tqdm.tqdm(dataset):
        messages = [{"role": "system", "content": prompt.format(profile = data["user_profile"], platforms = data["platforms"], tools = data["tools"], format = format)},
                {"role": "user", "content": data["query"]}
                ]
        completion = client.chat.completions.create(
            model = kwargs["api_model_name"],
            messages = messages
        )

        with open(output_dir +'/'+test_dir+"/generation.jsonl", "a") as f:
            json.dump({"query":data["query"], 
                    "label":data["answer"],
                    "predict":str(completion.choices[0].message.content)}, f)
            f.write('\n')
