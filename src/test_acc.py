import csv
import json
from .parse import ast_parse

def include(x,y):
    if x == 'true' or x == 'false':
        return json.loads(x) in y
    elif isinstance(x, bool):
        return x in y
    elif isinstance(x, str):
        z = [i.lower() for i in y]
        return x.lower() in z
    elif isinstance(x, list):
        x = set([i.lower() for i in x])
        z = [set([i.lower() for i in j]) for j in y]
        return set(x) in z
    elif isinstance(x, int):
        z = y[0]
        return x<=z+0.01 and x>=z-0.01
    return x in y

def evaluate(real, predict, params):

    real_platform, real_funcs = real
    predict_platform, predict_funcs = predict

    overall_acc = 1
    platform_acc = 1
    funcname_acc = 1
    arg_acc = 1
    func_acc = 1
    
    query_param_acc = 0
    profile_param_acc = 0

    if real_platform != predict_platform:
        platform_acc = 0
        overall_acc = 0
    

    #if predict in real
    real_func_names = [list(real_func.keys())[0] for real_func in real_funcs]
    for predict_func in predict_funcs:
        predict_func_name = list(predict_func.keys())[0]
        if predict_func_name in real_func_names:
            pos = real_func_names.index(predict_func_name)
            real_param_names = list(real_funcs[pos][predict_func_name].keys())
            for predict_param_name, predict_param_value in list(predict_func.values())[0].items():
                if predict_param_name in real_param_names:
                    real_param_value = real_funcs[pos][predict_func_name][predict_param_name]
                    if include(predict_param_value, real_param_value):
                        if predict_param_name in params["query_params"]:
                            query_param_acc += 1
                        elif predict_param_name in params["profile_params"]:
                            profile_param_acc += 1
                    else:
                        func_acc = 0
                        overall_acc = 0
                else:
                    arg_acc = 0
                    func_acc = 0
                    overall_acc = 0
        else:
            funcname_acc = 0
            arg_acc = 0
            func_acc = 0
            overall_acc = 0



    #if real in predict
    predict_func_names = [list(predict_func.keys())[0] for predict_func in predict_funcs]
    for real_func in real_funcs:
        real_func_name = list(real_func.keys())[0]
        if real_func_name in predict_func_names:
            pos = predict_func_names.index(real_func_name)
            predict_param_names = list(predict_funcs[pos][real_func_name].keys())
            for real_param_name, real_param_value in list(real_func.values())[0].items():
                if real_param_name in predict_param_names:
                    predict_param_value = predict_funcs[pos][real_func_name][real_param_name]
                    if not include(predict_param_value, real_param_value):
                        func_acc = 0
                        overall_acc = 0
                else:
                    arg_acc = 0
                    func_acc = 0
                    overall_acc = 0
        else:
            funcname_acc = 0
            arg_acc = 0
            func_acc = 0
            overall_acc = 0

    return overall_acc, platform_acc, funcname_acc, arg_acc, func_acc, query_param_acc, profile_param_acc

def cal_acc(test_type, output_dir):
    with open(test_type+'/data.json', 'r') as f:
        real = json.load(f)
    with open(output_dir+'/'+test_type+'/generation.jsonl', "r") as f:
        predict = f.readlines()
    predict = [json.loads(i)["predict"] for i in predict]

    format_acc = 0
    overalls_acc = 0
    platforms_acc = 0
    funcnames_acc = 0
    args_acc = 0
    funcs_acc = 0
    query_params_acc = 0
    profile_params_acc = 0
    query_params_num = 0
    profile_params_num = 0

    for i in range(len(real)):
        real_answer = real[i]["answer"]
        params = {key: real[i][key] for key in ["query_params", "profile_params"]}
        query_params_num += len(params["query_params"])
        profile_params_num += len(params["profile_params"])
        try:
            predict_answer = ast_parse(predict[i])
            overall_acc, platform_acc, funcname_acc, arg_acc, func_acc, query_param_acc, profile_param_acc = evaluate(real_answer, predict_answer, params)
            format_acc += 1
            overalls_acc += overall_acc
            platforms_acc += platform_acc
            funcnames_acc += funcname_acc
            args_acc += arg_acc
            funcs_acc += func_acc
            query_params_acc += query_param_acc
            profile_params_acc += profile_param_acc
        except Exception as e:
            continue


    with open(output_dir + '/'+ test_type +"/acc_results.csv", "w") as f:
        writer = csv.writer(f)
        name = ["format", "platforms", "tool_names", "tool_param_names", "tool_param_values", "query_params", "profile_params", "overall"]
        writer.writerow(name)

        value = [format_acc / len(real),
                 (platforms_acc / len(real)),
                 (funcnames_acc / len(real)),
                 (args_acc / len(real)),
                 (funcs_acc / len(real)),
                 (query_params_acc / query_params_num),
                 (profile_params_acc / profile_params_num),
                 (overalls_acc / len(real))
                 ]
        writer.writerow(value)
    