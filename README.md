
<h1 align="center">PTBench</h1><hr>


<h2> Table of contents</h2>

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Evaluating OSS Model](#evaluating-oss-model)
- [Evaluating API Model](#evaluating-api-model)
- [Viewing Results](#viewing-results)
- [Additional Help](#additional-help)
- [Updating Leaderboard](#updating-leaderboard)


## Introduction


We develop a systematic personalized data synthesis framework and construct PTBench, the first benchmark for personalized tool invocation, enabling a comprehensive evaluation of models' ability to invoke tools based on user information.

See the live leaderboard at [PTBench](https://huggingface.co/spaces/ustchyf/PTBench)

## Quick Start



### Installation

```bash
# Create a new Conda environment with Python 3.9
conda create -n PTBench python=3.9
conda activate PTBench

# Clone the PTBench repository
git clone --depth 1 https://github.com/hyfshadow/PTBench.git

# change the directory to PTBench
cd PTBench

#install the packages
pip install -r requirements.txt
```

## Evaluating OSS Model


### Set Up


set up your config in [`config.yaml`](config.yaml) .

If you want to change more specific parameters, such as temperature, you can edit the code in [`src/predict_oss.py`](src/predict_oss.py). 



### Supported OSS Model


|  model   | template  |
|  ----  | ----  |
| Qwen2.5  | qwen |
| Llama 3  | llama3 |
| Mistral | mistral |
| xLAM  | xlam |
| hammer  | hammer |
| deepseek R1(Distill)  | deepseek3 |

> You can add unsupported models. To see specifics, read [Addtional Help](#additional-help).



### run evaluation


```bash
python run.py --type oss
```

## Evaluating API models


### Set Up

set up your api key and base url in [`config.yaml`](config.yaml).

If you want to change more specific parameters, such as temperature, you can edit the code in [`src/predict_api.py`](src/predict_api.py). 

<b>ATTENTION</b>: We only support openai API


### run evaluation


```bash
python run.py --type api
```

## Viewing Results
You can find your results in your given `output_dir` repository. The reult is divided into three part, untrained-user, trained-user and overall, each containing accuaracy and error analysis results. For more specific details, you can read our paper.


## Additional Help

### Adding unsupported models
You can add the template in [`src/template.py`](src/template.py).

If your model's template is similar to those of qwen, only varying in tokenizers' forms, you can use the given prompt directly. Otherwise, you will need to difine your own function `return_prompt()` and use it in the function `register_template()`, such as in the template of xLAM.

### Changing answer format
You can change the format of the answer in `src/template.py` to fit your model better. You should also change the way you parse the answer in `src/parser.py`. We already realized a second way of parsing the format of `{'platform':platform_name. 'functions':[{'name':func1_name, parameters:{param1_name:param1_value, param2...}}, func2...]` in the function `ast_parse_2()`

## Updating Leaderboard
If you want to show your results in the leaderboard, you can sent an email to huang_yuefeng@mail.ustc.edu.cn. Your email should contain your public model name on huggingface and your evaluation results `.csv` files.