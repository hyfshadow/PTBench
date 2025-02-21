import csv
import os

def conclude(output_dir):
    with open(output_dir + '/test_untrained_user/acc_results.csv') as f:
        un_acc_reader = csv.reader(f)
        un_acc = list(un_acc_reader)
    with open(output_dir + '/test_untrained_user/error_results.csv') as f:
        un_error_reader = csv.reader(f)
        un_error = list(un_error_reader)

    with open(output_dir + '/test_trained_user/acc_results.csv') as f:
        acc_reader = csv.reader(f)
        acc = list(acc_reader)
    with open(output_dir + '/test_trained_user/error_results.csv') as f:
        error_reader = csv.reader(f)
        error = list(error_reader)


    overall_acc = [acc[0], [(float(un_acc)*609+float(acc)*474)/1083 for un_acc, acc in zip(un_acc[1], acc[1])]]
    overall_error = [error[0], [int(un_error)+int(error) for un_error, error in zip(un_error[1], error[1])]]

    if not os.path.exists(output_dir + "/overall"):
        os.makedirs(output_dir + "/overall")

    with open(output_dir + "/overall/acc_results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(overall_acc)

    with open(output_dir + "/overall/error_results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(overall_error)
        