import yaml
from src.test_acc import cal_acc
from src.test_error import cal_error
from src.predict_oss import predict_oss
from src.predict_api import predict_api
from src.overall import conclude
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str, default = 'oss')
args = parser.parse_args()
type = args.type

with open('config.yaml', 'r') as file:
    content = file.read()

config = yaml.safe_load(content)

for dir in ["test_untrained_user", "test_trained_user"]:
    config["test_dir"] = dir
    if type=='oss':
        predict_oss(**config)
    else:
        predict_api(**config)
    cal_acc(dir, config["output_dir"])
    cal_error(dir, config["output_dir"])

conclude(config["output_dir"])


