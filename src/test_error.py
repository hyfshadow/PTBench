from .parse import ast_parse
import json
import csv

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

def error_analysis(real, predict, params):
    real_platform, real_funcs = real
    predict_platform, predict_funcs = predict

    platform_error = 0
    func_lack_error = 0
    func_excess_error = 0
    param_lack_error = 0
    param_excess_error = 0
    value_error = 0
    query_value_error = 0
    profile_value_error = 0

    if real_platform != predict_platform:
        platform_error = 1
    
    #excess_detect
    predict_func_names = [list(predict_func.keys())[0] for predict_func in predict_funcs]
    for real_func in real_funcs:
        real_func_name = list(real_func.keys())[0]
        if real_func_name in predict_func_names:
            pos = predict_func_names.index(real_func_name)
            real_param_names = list(real_func[real_func_name].keys())
            predict_param_names = list(predict_funcs[pos][real_func_name].keys())
            for real_param_name, real_param_value in list(real_func.values())[0].items():
                if real_param_name in predict_param_names:
                    predict_param_value = predict_funcs[pos][real_func_name][real_param_name]
                    if not include(predict_param_value, real_param_value):
                        value_error = 1
                        if real_param_name in params["query_params"]:
                            query_value_error = 1
                        elif real_param_name in params["profile_params"]:
                            profile_value_error = 1
                else:
                    param_excess_error = 1
        else:
            func_excess_error = 1
    
    #lack_detect
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
                        continue
                else:
                    if predict_param_name in params["query_params"]:
                        query_value_error = 1
                    elif predict_param_name in params["profile_params"]:
                        profile_value_error = 1
                    param_lack_error = 1
        else:
            func_lack_error = 1

    return platform_error, func_lack_error, func_excess_error, param_lack_error, param_excess_error, value_error, query_value_error, profile_value_error

def cal_error(test_type, output_dir):
    with open(test_type+'/data.json', 'r') as f:
        real = json.load(f)
    with open(output_dir+'/'+test_type+'/generation.jsonl', "r") as f:
        predict = f.readlines()
    predict = [json.loads(i)["predict"] for i in predict]

    format_errors = 0
    platform_errors = 0
    func_wrong_errors = 0
    func_lack_errors = 0
    func_excess_errors = 0
    param_lack_errors = 0
    param_excess_errors = 0
    value_errors = 0
    query_value_errors = 0
    profile_value_errors = 0

    for i in range(len(real)):
        real_answer = real[i]["answer"]
        params = {key: real[i][key] for key in ["query_params", "profile_params"]}
        try:

            predict_answer = ast_parse(predict[i])
            platform_error, func_lack_error, func_excess_error, param_lack_error, param_excess_error, value_error, query_value_error, profile_value_error = error_analysis(real_answer, predict_answer, params)
            func_error = func_lack_error or func_excess_error
            param_error = param_lack_error or param_excess_error

            platform_errors += platform_error
            func_wrong_errors += func_lack_error and func_excess_error
            func_lack_errors += func_lack_error and not func_excess_error
            func_excess_errors += func_excess_error and not func_lack_error
            param_lack_errors += param_lack_error and not func_error
            param_excess_errors += param_excess_error and not func_error
            value_errors += value_error and not func_error and not param_error
            query_value_errors += query_value_error
            profile_value_errors += profile_value_error

        except Exception as e:
            format_errors += 1
    
    with open(output_dir + '/'+ test_type +"/error_results.csv", "w") as f:
        writer = csv.writer(f)
        name = ["func_wrong_error", "func_missing_error", "func_excessive_error", "param_missing_error", "param_excessive_error", "value_error"]
        writer.writerow(name)

        value = [func_wrong_errors,
                func_lack_errors,
                func_excess_errors,
                param_lack_errors,
                param_excess_errors,
                value_errors
                 ]
        writer.writerow(value)
