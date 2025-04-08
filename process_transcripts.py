#!/usr/bin/env python

import json
from ollama import chat
import re
# import transcripts_download as TD
import pandas as pd
from pydantic import BaseModel

# Example to remove tag from text with Regular Expressions
# import re
# Ollama response
# response = response["message"]["content"]
# Remove Think Tag from Text with Regular Expressions
# cleaned_content = re.sub(r"<think>.*?</think>\n?", "", response,
# flags=re.DOTALL)


class Output(BaseModel):
    sentiment: float
    confidence: float
    reason: str


def get_sentiment(person, text, model=None):
    omodel = model
    if model is None:
        # XXX: This is just to avoid going over boundary
        smodel = "gemma-2/gemma-2-sentiment_analysis_with_reasoning:2b-f16"
        model = "seandearnaley"+smodel
    else:
        model = model
        ftext = r"you are an assistant that performs sentiment analysis. Given text you will give a sentiment score between -1 and 1 for negative to  positive. You will also give a confidence score between 0 and 1 for no confidence to very confident. Finally, you will give a reason in 1-2 sentence describing the reason for your sentiment score. You will only give the sentiment score, confidence score, and reason as output in json format."
    if omodel is not None:
        text = ftext + "text: " + text
        # XXX: First set the role of ollama
    print('Person: %s' % person, end=' ', flush=True)
    print('size of text: ', len(text), end=' ', flush=True)
    print('Model: ', model)
    mresponse = list()
    count = 0
    for response in chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },],
                         format=Output.model_json_schema(),
                         stream=True):
        # print(response['message']['content'], end='', flush=True)
        count += 1
        if count > 1000:
            break
        if response['message']['content'].startswith('###'):
            break
        mresponse.append(response['message']['content'])
    try:
        response = ''.join(mresponse)
        # print(response)
        # assert (False)
        res = json.loads(response)['sentiment']
        rc = json.loads(response)['confidence']
    except Exception:
        print('Exception occured: %s' % ' '.join(mresponse))
        res = 0
        rc = 0

    print(' sentiment score: ', res, 'confidence: ', rc)
    return res, rc


def process(f, others, model):
    print('Processing: ', f)
    # XXX: Dictionary of every text
    sayings = dict()
    with open(f) as json_data:
        d = json.load(json_data)
        json_data.close()
        if len(d) == 0:
            return {}
        # XXX: There can be spurious newlines in the text!
        strings = re.split("\\n([a-z|A-Z]+)", (d[0]['content']))
        # strings = ((d[0]['content'])).split('\n')
        ps = None
        for s in strings:
            kv = s.split(':')
            if len(kv) > 1:
                kk = ps + kv[0] if ps is not None else kv[0]
                if kk in sayings.keys():
                    sayings[kk].append([kv[1]])
                else:
                    sayings[kk] = [[kv[1]]]
            else:
                ps = s
                # XXX: Now go through the sayings and get the sentiment
                # for each person on the call.
    sentiments = {'date': d[0]['date']}
    for s in sayings:
        if s not in others:
            print('Processing person: ', s, 'total sayings: ', len(sayings[s]))
            s_score = [get_sentiment(s, v[0], model) for v in sayings[s]]
            sentiment_score = [float(s[0]) for s in s_score]
            confidence_score = [float(s[1]) for s in s_score]
            # XXX: The average sentiment score for this person in the call
            sentiments[s] = {'avg_sentiment_score':
                             sum(sentiment_score)/len(sentiment_score),
                             'sentiment_score': sentiment_score,
                             'avg_confidence':
                             sum(confidence_score)/len(confidence_score),
                             'confidence': confidence_score}
    return sentiments


if __name__ == '__main__':
    years = list(range(2010, 2025))
    quarters = list(range(1, 5))
    # XXX: The companies that are done

    sp500 = [x.strip() for x in list(pd.read_csv('sp500.csv')['Symbol'])]
    others = ['Executives', 'Operator', 'Analysts']
    models = [  # 'llama3.2',
              'deepseek-r1']
    for model in models:
        done_df = [x.strip()
                   for x in
                   list(pd.read_csv('done_%s.csv' % model)['Companies'])]
        for c in sp500:
            if c in done_df:
                print('Already Done: ', c)
                continue
        # XXX: First download the transcript
        # TD.main(c)
        # XXX: Now process the downloaded files
            for y in years:
                for q in quarters:
                    senscore = process(
                        './transcripts/%s_Q%s_%s' % (c, q, y), others,
                        model=model)
                    with open('./transcript_scores_%s/%s_Q%s_%s.json'
                              % (model, c, q, y), 'w') as f:
                        json.dump(senscore, f)
        # XXX: Append to the done company list too
        done_df.append(c)
        # XXX: Write the done company name to done.csv
        with open('./done_%s.csv' % model, 'a+') as f:
            f.write(c+'\n')
        print('Processed and wrote: ', c)
