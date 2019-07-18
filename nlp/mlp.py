"""Taken from:
https://developers.google.com/machine-learning/guides/text-classification/step-4

Usage: 
    data = comments_with_classification()
    train_ngram_model(data)
"""

import emoji
import random
import tensorflow

import constants
import mongo_handler

from tensorflow.python.keras import models
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Dropout

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

# Vectorization parameters
# Range (inclusive) of n-gram sizes for tokenizing text.
NGRAM_RANGE = (1, 2)

# Limit on the number of features. We use the top 20K features.
TOP_K = 20000

# Whether text should be split into word or character n-grams.
# One of 'word', 'char'.
TOKEN_MODE = 'word'

# Minimum document/corpus frequency below which a token will be discarded.
MIN_DOCUMENT_FREQUENCY = 2

# Vector translation for features.
POSITIVITY_VECTORIZATION = dict(zip(
    constants.POSITIVITY_TEXT.keys(), 
    list(range(len(constants.POSITIVITY_TEXT)))
))

CATEGORY_VECTORIZATION = dict(zip(
    constants.CATEGORIES_TEXT.keys(),
    list(range(len(constants.CATEGORIES_TEXT)))
))

                
def _convert_emoji(s):
    """Used to convert emojis in text to a simplified string.

    The emoji library converts 🌊  to :water_wave:
    We modify the delimiter to a character that the vectorizer will retain, and
        add the space to ensure each emoji is seperate.
    """
    return emoji.demojize(s, delimiters=('_', '_ '))

# TODO: to begin with, we will ignore metadata
def comments_with_classification(mode=constants.POSITIVITY):
    """Preps comments and their label for the model.
    
    Retrieves comment body from comment and vectorizes the label. Additionally 
    converts all emojis in the comment body to ascii strings.

    # Arguments
        mode: string, what classification are we looking for?

    # Returns: 
        A tuple of all comment bodies with their corresponding label.
    """
    texts, vectorized_labels = [], []
    if mode == constants.POSITIVITY: 
        classified_comments = mongo_handler.classified_comments_with_positivity()
        for comment, label in classified_comments:
            texts.append(_convert_emoji(comment['body']))
            vectorized_labels.append(POSITIVITY_VECTORIZATION[label])
    elif mode == constants.CATEGORY:
        classified_comments = mongo_handler.classified_comments_with_category()
        for comment, label in classified_comments:
            texts.append(_convert_emoji(comment['body']))
            vectorized_labels.append(CATEGORY_VECTORIZATION[label])
    else: 
        raise ValueError(f'You must request classification of either '
                '{constants.POSITIVITY} or constants.CATEGORY}')

    # TODO: shuffle these together
    cutoff = int(len(texts) * .7)
    return (texts[:cutoff], vectorized_labels[:cutoff]), (texts[cutoff:], vectorized_labels[cutoff:])

def create_ngram_vectorizer():
    """Create a vectorizer: a tool that translates the corpus into vectors.

    1 text = 1 tf-idf vector the length of vocabulary of unigrams & bigrams.

    # Returns
        instance of tf-idf vectorizer.
    """
    # Create keyword arguments to pass to the tf-idf vectorizer.
    kwargs = {
            'ngram_range': NGRAM_RANGE, # Use 1-grams & 2-grams.
            'dtype': 'int32',
            'strip_accents': 'unicode',
            'decode_error': 'replace',
            'analyzer': TOKEN_MODE, # Split text into word tokens.
            'min_df': MIN_DOCUMENT_FREQUENCY,
        }
    return TfidfVectorizer(**kwargs)

def fit_vectorizer(train_texts, vectorizer):
    """Sets up the vectorizer using the train texts.
    
    # Arguments
        train_texts: list, training text strings.
        vectorizer: the sklearn vectorizer to fit.

    # Returns
        x_train: vectorized train texts.
    """
    print("Fitting vectorizer and applying to train texts.")
    return vectorizer.fit_transform(train_texts)

def vectorize_texts(texts, vectorizer):
    """Applies vectorizer to texts
    
    # Arguments
        texts: list, text strings to be vectorized.
        vectorizer: the sklearn vectorizer that has already been fitted.

    # Returns
        x_text: vectorized text
    """
    # TODO: have check for if vectorizer is fitted?
    print("Vectorizing text...")
    return vectorizer.transform(texts)

def create_selector(k):
    """The selector selects the top 'k' of the vectorized features.
    
    # Arguments
        x_train: vectorized text
        k: int, max number of features

    # Returns
        selector: sklearn SelectKBest instance
    """
    print(f"Selecting top {k} vectorized features...")
    return SelectKBest(f_classif, k=k)


def ngram_vectorize(train_texts, train_labels, val_texts):
    vectorizer = create_ngram_vectorizer()
    x_train = fit_vectorizer(train_texts, vectorizer)
    x_val = vectorize_texts(val_texts, vectorizer)

    selector = create_selector(min(TOP_K, x_train.shape[1]))
    selector.fit(x_train, train_labels)
    x_train = selector.transform(x_train).astype('float32')
    x_val = selector.transform(x_val).astype('float32')
    return x_train, x_val


def get_num_classes(labels):
    """Gets the total number of classes.
    # Arguments
        labels: list, label values.
            There should be at lease one sample for values in the
            range (0, num_classes -1)
    # Returns
        int, total number of classes.
    # Raises
        ValueError: if any label value in the range(0, num_classes - 1)
            is missing or if number of classes is <= 1.
    """
    num_classes = max(labels) + 1
    missing_classes = [i for i in range(num_classes) if i not in labels]
    if len(missing_classes):
        raise ValueError('Missing samples with label value(s) '
                         '{missing_classes}. Please make sure you have '
                         'at least one sample for every label value '
                         'in the range(0, {max_class})'.format(
                            missing_classes=missing_classes,
                            max_class=num_classes - 1))

    if num_classes <= 1:
        raise ValueError('Invalid number of labels: {num_classes}.'
                         'Please make sure there are at least two classes '
                         'of samples'.format(num_classes=num_classes))
    return num_classes


def _get_last_layer_units_and_activation(num_classes):
    """Gets the # units and activation function for the last network layer.

    # Arguments
        num_classes: int, number of classes

    # Returns
        units, activation values
    """

    if num_classes == 2:
        activation = 'sigmoid'
        units = 1
    else:
        activation = 'softmax'
        units = num_classes
    return units, activation


def mlp_model(layers, units, dropout_rate, input_shape, num_classes):
    """Creates an instance of a multi-layer perceptron model.

    # Arguments
        layers: int, number of 'Dense' layers
        units: int, output dimension of layers
        dropout_rate: float, pcntg of input to drop at Dropout layers
        input_shape: tuple, shape of input to the model
        num_classes: int, number of output classes

    # Returns
        An MLP model instance
    """
    op_units, op_activation = _get_last_layer_units_and_activation(num_classes)
    model = models.Sequential()
    model.add(Dropout(rate=dropout_rate, input_shape=input_shape))

    for _ in range(layers - 1):
        model.add(Dense(units=units, activation='relu'))
        model.add(Dropout(rate=dropout_rate))

    model.add(Dense(units=op_units, activation=op_activation))
    return model

def train_ngram_model(data,
                      learning_rate=1e-3,
                      epochs=1000,
                      batch_size=128,
                      layers=2,
                      units=64,
                      dropout_rate=0.2):
    """Trains n-gram model on the given dataset.

    # Arguments
        data: tuples of training and test texts and labels.
        learning_rate: float, learning rate for training model.
        epochs: int, number of epochs.
        batch_size: int, number of samples per batch.
        layers: int, number of `Dense` layers in the model.
        units: int, output dimension of Dense layers in the model.
        dropout_rate: float: percentage of input to drop at Dropout layers.

    # Raises
        ValueError: If validation data has label values which were not seen
            in the training data.
    """
    # Get the data.
    (train_texts, train_labels), (val_texts, val_labels) = data

    # Verify that validation labels are in the same range as training labels.
    num_classes = get_num_classes(train_labels)
    unexpected_labels = [v for v in val_labels if v not in range(num_classes)]
    if len(unexpected_labels):
        raise ValueError('Unexpected label values found in the validation set:'
                         ' {unexpected_labels}. Please make sure that the '
                         'labels in the validation set are in the same range '
                         'as training labels.'.format(
                             unexpected_labels=unexpected_labels))

    # Vectorize texts.
    x_train, x_val = ngram_vectorize(train_texts, train_labels, val_texts)


    # Create model instance.
    model = mlp_model(layers=layers,
                      units=units,
                      dropout_rate=dropout_rate,
                      input_shape=x_train.shape[1:],
                      num_classes=num_classes)

    # Compile model with learning parameters.
    if num_classes == 2:
        loss = 'binary_crossentropy'
    else:
        loss = 'sparse_categorical_crossentropy'
    optimizer = tensorflow.keras.optimizers.Adam(lr=learning_rate)
    model.compile(optimizer=optimizer, loss=loss, metrics=['acc'])

    # Create callback for early stopping on validation loss. If the loss does
    # not decrease in two consecutive tries, stop training.
    callbacks = [tensorflow.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=2)]

    # Train and validate model.
    history = model.fit(
            x_train,
            train_labels,
            epochs=epochs,
            callbacks=callbacks,
            validation_data=(x_val, val_labels),
            verbose=2,  # Logs once per epoch.
            batch_size=batch_size)

    # Print results.
    history = history.history
    print('Validation accuracy: {acc}, loss: {loss}'.format(
            acc=history['val_acc'][-1], loss=history['val_loss'][-1]))

    # Save model.
    model.save('IMDb_mlp_model.h5')
    return history['val_acc'][-1], history['val_loss'][-1]

