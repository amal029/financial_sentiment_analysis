#!/usr/bin/env python

import json
from ollama import chat
import re
import transcripts_download as TD
import pandas as pd


def get_sentiment(person, text):
    model = "seandearnaley/gemma-2-sentiment_analysis_with_reasoning:2b-f16"
    print('Person: %s' % person, end=' ', flush=True)
    print('size of text: ', len(text), end='', flush=True)
    mresponse = list()
    count = 0
    for response in chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },], stream=True):
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
        res = json.loads(response)['sentiment']
        rc = json.loads(response)['confidence']
    except Exception:
        print('Exception occured: %s' % ' '.join(mresponse))
        res = 0
        rc = 0

    print(' sentiment score: ', res, 'confidence: ', rc)
    return res, rc


def process(f, others):
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
    # XXX: Now go through the sayings and get the sentiment for each
    # person on the call.
    sentiments = {'date': d[0]['date']}
    for s in sayings:
        if s not in others:
            print('Processing person: ', s, 'total sayings: ', len(sayings[s]))
            s_score = [get_sentiment(s, v[0]) for v in sayings[s]]
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
    done_df = [x.strip() for x in list(pd.read_csv('done.csv')['Companies'])]
    sp500 = [x.strip() for x in list(pd.read_csv('sp500.csv')['Symbol'])]
    others = ['Executives', 'Operator', 'Analysts']
    for c in sp500:
        if c in done_df:
            print('Already Done: ', c)
            continue
        # XXX: First download the transcript
        TD.main(c)
        # XXX: Now process the downloaded files
        for y in years:
            for q in quarters:
                senscore = process(
                    './transcripts/%s_Q%s_%s' % (c, q, y), others)
                with open('./transcript_scores/%s_Q%s_%s.json'
                          % (c, q, y), 'w') as f:
                    json.dump(senscore, f)
        # XXX: Append to the done company list too
        done_df.append(c)
        # XXX: Write the done company name to done.csv
        with open('./done.csv', 'a') as f:
            f.write(c+'\n')
        print('Processed and wrote: ', c)
