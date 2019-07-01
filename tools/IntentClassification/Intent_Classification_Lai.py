#!/usr/bin/env python
# coding: utf-8

# Import the dependencies
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from keras import layers
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Bidirectional, Embedding, Dropout
from keras.callbacks import ModelCheckpoint
from keras.models import model_from_json
import pickle

#Define functions (also for importing)
def readdata(filename):
    return pd.read_csv(filename, names = ["message", "Intent"],encoding = "latin1")

def cleaning(sentences):
    words = []
    for s in sentences:
        clean = re.sub(r'[^ a-z A-Z 0-9]', " ", s)
        w = word_tokenize(clean)
        #stemming
        words.append([i.lower() for i in w])
    return words

def create_tokenizer(words, filters = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'):
    token = Tokenizer(filters = filters)
    token.fit_on_texts(words)
    return token

def maximum_length(words):
    return(len(max(words, key = len)))

def encoding_doc(token, words):
    return(token.texts_to_sequences(words))

def padding_doc(encoded_doc, max_length):
    return(pad_sequences(encoded_doc, maxlen = int(max_length), padding = "post"))

def one_hot(encode):
    o = OneHotEncoder(sparse = False)
    return(o.fit_transform(encode))

def create_model(vocab_size, max_length):
    model = Sequential()
    model.add(Embedding(vocab_size, 128, input_length = max_length, trainable = False))
    model.add(Bidirectional(LSTM(128)))
    model.add(Dense(32, activation = "relu"))
    model.add(Dropout(0.5))
    model.add(Dense(intentsize, activation = "softmax"))
    return model

def predictions(word_tokenizer, text, model, max_length=30):
    clean = re.sub(r'[^ a-z A-Z 0-9]', " ", text)
    test_word = word_tokenize(clean)
    test_word = [w.lower() for w in test_word]
    test_ls = word_tokenizer.texts_to_sequences(test_word)
    #Check for unknown words
    if [] in test_ls:
        test_ls = list(filter(None, test_ls))
    test_ls = np.array(test_ls).reshape(1, len(test_ls))
    x = padding_doc(test_ls, max_length)
    pred = model.predict_proba(x)
    return pred

#Function to output predictions
def get_final_output(pred, classes, mode):
    predictions = pred[0]
    classes = np.array(classes)
    ids = np.argsort(-predictions)
    classes = classes[ids]
    predictions = -np.sort(-predictions)
    if mode == 'rank':
        for i in range(pred.shape[1]):
            print("%s has confidence = %s" % (classes[i], (predictions[i])))
    elif mode == 'classify':
        return classes[0]

if __name__ == "__main__":
    #Extract Dataset
    filename = 'datasets/Preliminary_Dataset.csv'
    trainingdata = readdata(filename)
    messages = trainingdata['message']
    intent = trainingdata['Intent']
    unique_intent = list(set(intent))

    #Process x values
    #Cleaning messages, removing numbers and
    words = cleaning(messages)

    #Tokenizing messages
    word_tokenizer = create_tokenizer(words)
    #Saving tokenizer for other files
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(word_tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #Figure out vocabulary size
    vocab_size = len(word_tokenizer.word_index) + 1

    #Find the max length of a message
    max_length = maximum_length(words)
    #print("Vocab Size = %d and Maximum length = %d" % (vocab_size, max_length))
    #Save the max length to a file
    with open('maxlen.txt', 'w') as file:
        file.write(str(max_length))

    #Created a document that can be inputted in Keras
    encoded_doc = encoding_doc(word_tokenizer,words)
    padded_doc = pad_sequences(encoded_doc, maxlen = max_length, padding = "post")
    #print(padded_doc)

    #Process Outputs
    #Tokenize intentions
    output_tokenizer=create_tokenizer(unique_intent,filters = '!"#$%&()*+,-/:;<=>?@[\]^`{|}~')
    #output_tokenizer.word_index

    #Number of unique intents
    intentsize = len(unique_intent)

    #Encode output for keras
    encoded_output =  encoding_doc(output_tokenizer,intent)
    encoded_output = np.array(encoded_output).reshape(len(encoded_output), 1)

    #make onehot output
    output_one_hot = one_hot(encoded_output)

    x_train, x_test, y_train, y_test = train_test_split(padded_doc, output_one_hot, shuffle = True, test_size=0.2, random_state=1000)

    #Model Creation
    model = create_model(vocab_size, max_length)

    model.compile(loss = "categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])
    model.summary()

    # Fit the model to the training data
    filename = 'model_weights.h5'
    checkpoint = ModelCheckpoint(filename, monitor='val_loss', verbose=1, save_best_only=True, mode='min')

    hist = model.fit(x_train, y_train, epochs = 20, batch_size = 32, validation_data = (x_test, y_test), callbacks = [checkpoint])

    model.save_weights('model_weights.h5')
    # Save the model architecture
    with open('model_architecture.json', 'w') as f:
        f.write(model.to_json())

    # Load our proudly trained model
    with open('model_architecture.json', 'r') as f1:
        model = model_from_json(f1.read())
