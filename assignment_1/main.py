import os
import numpy as np
import tensorflow as tf
from clustering import PhraseClustering
from io_tools import read_dataset, read_phrase_list
from metrics import bottom_k, mid_k, top_k

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_integer('n_clusters', 40, 'Number of clusters to be found')
flags.DEFINE_string('filename', None,
                    'Path to the file containing the phrases to be clustered')
flags.DEFINE_string('data_folder', None, 'Folder where the files are located')
flags.DEFINE_string('distance', 'cosine',
                    'Distance function used to compare the vectors')
flags.DEFINE_string('task', 'metrics',
                    'Define which task this script should perform. '
                    'Accepts: ["metrics", "clustering"]')
flags.DEFINE_integer('k', 30, 'Number of top/bottom results reported')
flags.DEFINE_string('output', 'metrics.txt',
                    'Where the metrics will be saved. '
                    'Only used when task=metrics')


def main(_):
    data_folder = FLAGS.data_folder
    filename = FLAGS.filename

    if FLAGS.task == 'metrics':
        output = FLAGS.output
        k = FLAGS.k
        # find top-k, mid-k and bottom-k
        scores, phrases = read_phrase_list(data_folder=data_folder,
                                           filename=filename)
        bottom = bottom_k(scores, phrases, k=k)
        mid = mid_k(scores, phrases, k=k)
        top = top_k(scores, phrases, k=k)

        with open(data_folder + '/' + output, 'w') as out:
            out.write('Bottom-k (' + str(k) + ')' + '\n')
            for entry in bottom:
                out.write(entry)
            out.write('\n')

            out.write('Mid-k (' + str(k) + ')' + '\n')
            for entry in mid:
                out.write(entry)
            out.write('\n')

            out.write('Top-k (' + str(k) + ')' + '\n')
            for entry in top:
                out.write(entry)

    elif FLAGS.task == 'clustering':
        print('Current step: Reading data set', end='\r')
        y_train, x_train = read_dataset(filename=filename,
                                        data_folder=data_folder)

        print('Current step: Performing clustering', end='\r')
        task = PhraseClustering()
        y_pred = task.run(x_train, n_clusters=FLAGS.n_clusters,
                          distance=FLAGS.distance)

        # create result files
        print('Current step: Saving clustered phrases', end='\r')
        clusters_folder = data_folder + '/clusters'
        if not os.path.exists(clusters_folder):
            os.makedirs(data_folder + '/clusters')

        cluster_ids = np.unique(y_pred)
        files = {}
        for cluster in cluster_ids:
            out = open(data_folder + '/clusters' + '/cluster' + str(cluster), 'w')
            files[cluster] = out

        for i, cluster in enumerate(y_pred.tolist()):
            files[cluster].write(y_train[i] + '\n')

        for _, file in files.items():
            file.close()


if __name__ == '__main__':
    tf.app.run()