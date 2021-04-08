
import scipy.stats
import numpy as np
from prepData.dataLoader import *
import pickle
import matplotlib.pyplot as plt


def tableResults(pickle_path, windows_OS, experiment_name):
    # fold, artifact, model, scores
    results = LoadNumpyPickles(pickle_path=pickle_path, file_name = r'\results'+ experiment_name +'.npy', windowsOS = windowsOS)
    results = results[()]
    # fold, artifact, model, hyperopt iterations
    HO_trials = LoadNumpyPickles(pickle_path=pickle_path, file_name = r'\ho_trials'+ experiment_name +'.npy', windowsOS = windowsOS)
    HO_trials = HO_trials[()]

    def mean_confidence_interval(data, confidence=0.95):
        a = 1.0 * np.array(data)
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
        return m-h, m, m+h



    pd.set_option("display.max_rows", None, "display.max_columns", None)

    table = {}
    table_std = {}

    # want to average each fold
    #construct keys
    folds = list(results.keys())
    artifacts = list(results[folds[0]].keys())
    models = list(results[folds[0]][artifacts[0]].keys())
    scores = list(results[folds[0]][artifacts[0]][models[0]].keys())

    # row-wise models, column-wise artifacts
    acc = np.zeros((len(models),len(artifacts)))
    acc_std = np.zeros((len(models),len(artifacts)))
    f1s = np.zeros((len(models),len(artifacts)))
    f1s_std = np.zeros((len(models),len(artifacts)))

    for idx_art, artifact in enumerate(artifacts):
        table[artifact] = []
        store_model = [0]*len(models)
        sensitivity_std = [0]*len(models)

        for idx_mod, model in enumerate(models):

            store_scores = []

            temp_acc = []
            temp_f1 = []
            for fold in folds:
                store_scores.append(results[fold][artifact][model]['sensitivity'])
                temp_acc.append(results[fold][artifact][model]['accuracy'])
                temp_f1.append(results[fold][artifact][model]['weighted_F1'])

            acc[idx_mod,idx_art] = np.mean(temp_acc)
            f1s[idx_mod,idx_art] = np.mean(temp_f1)

            # Standard deviation for acc. and F1 on each artifact
            acc_std[idx_mod, idx_art] = np.std(temp_acc)
            f1s_std[idx_mod, idx_art] = np.std(temp_f1)

        # Store standard deviation for sensitivies for each classifier/ model
        store_model[idx_mod] = np.mean(store_scores)
        sensitivity_std[idx_mod] = np.std(store_scores)

        table[artifact] = store_model
        table_std[artifact] = sensitivity_std


    table['avg. accuracy'] = np.mean(acc,axis=1)
    table['avg. weighted f1'] = np.mean(f1s,axis=1)

    # Mean standard deviation
    table_std['avg. accuracy'] = np.mean(acc_std, axis=1)
    table_std['avg. weighted f1'] = np.mean(f1s_std, axis=1)

    return table, table_std, models, artifacts


if __name__ == '__main__':
    dir = r"C:\Users\Albert Kjøller\Documents\GitHub\EEG_epilepsia"
    # pickle_path = r"/Users/Jacobsen/Documents/GitHub/EEG_epilepsia" + "/"
    windowsOS = True

    pickle_path = dir + r"\results"
    experiment_name = '_pilot_Adaboost'

    # Loading statistically calculated results as dictionaries
    performance, errors, model_names, artifact_names = tableResults(pickle_path=pickle_path, windows_OS=windowsOS, experiment_name=experiment_name)

    # Printing tables
    df_eval = pd.DataFrame.from_dict(performance)
    df_eval.index = model_names
    print('OVERALL PERFORMANCE\n')
    print(np.round(df_eval * 100, 2))
    # print(df_eval)

    df_eval = pd.DataFrame.from_dict(errors)
    df_eval.index = model_names
    print('\nSTANDARD DEVIATIONS\n')
    print(np.round(df_eval * 100, 2))


    save_path = dir + r'\Plots\Pilot'
    # Plotting results
    performance_vals = np.array(list(performance.values())[:6]).reshape(-1)
    error_vals = np.array(list(errors.values())[:6]).reshape(-1)
    plt.bar(x=artifact_names, height=performance_vals,width=0.5, color="lightsteelblue")
    plt.errorbar(x=artifact_names, y=performance_vals, yerr=error_vals, fmt='.',color='k')
    plt.title(model_names[0])
    plt.savefig(save_path + "\\" + model_names[0])
    plt.show()


    print("")


'''

model_names = [] # will be appended to

initial_data = {} # to construct dataframe

# if statements are used if the dict is originally empty
# we recursively add the rows for each model and end with overall performance
for model in CV_scores:
    model_names.append(model)

    #initialize for appending, momentary lists
    confidence = {} # confidence interval
    accuracies = []
    weighted_f1s = []

    for artifact in CV_scores[model]: # each artifact
        #add sensitivity to the data
        sensitivities = CV_scores[model][artifact]['sensitivity']

        if artifact_names[artifact] in initial_data:
            initial_data[artifact_names[artifact]].append(sensitivities.mean())
        else:
            initial_data[artifact_names[artifact]] = [sensitivities.mean()]

        minus, mean, plus = mean_confidence_interval(sensitivities)

        confidence[artifact_names[artifact]] = [minus, mean, plus]


        accuracies.append(CV_scores[model][artifact]['accuracy'].mean())
        weighted_f1s.append(CV_scores[model][artifact]['F1'].mean())

    #confidence
    minus, mean, plus = mean_confidence_interval(accuracies)
    confidence['accuracy'] = [minus, mean, plus]
    minus, mean, plus = mean_confidence_interval(weighted_f1s)
    confidence['weighted_f1'] = [minus, mean, plus]

    df_conf = pd.DataFrame.from_dict(confidence)
    df_conf.index = ['lower', 'mean', 'upper']
    df_conf.style.set_caption(model)
    print(df_conf)
    print('\n')

    # overall performance for all artifacts
    if 'accuracy' in initial_data:
        initial_data['accuracy'].append(np.mean(accuracies))
    else:
        initial_data['accuracy'] = [np.mean(accuracies)]

    if 'weighted_f1' in initial_data:
        initial_data['weighted_f1'].append(np.mean(weighted_f1s))
    else:
        initial_data['weighted_f1'] = [np.mean(weighted_f1s)]



#display all dataframe
pd.set_option("display.max_rows", None, "display.max_columns", None)

df_eval = pd.DataFrame.from_dict(initial_data)
df_eval.index = model_names
df_eval.style.set_caption("Overview")
print(df_eval)

print('\n\n')


'''

