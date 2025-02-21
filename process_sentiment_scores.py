#!/usr/bin/env python
from os import listdir
from os.path import isfile, join
import pandas as pd
import json
import re
import numpy as np
# import plotly.express as px


def append_sentiments(am, fname, cf, persons, sentiments):
    # XXX: If this blocks, that means you have repeated names in the
    # ceo/cfo list.
    kdict = [k for k in am[fname] if cf in k.keys()]
    assert (len(kdict) <= 1)
    if len(kdict) == 1:
        k = kdict[0]
        for x in sentiments[persons]['sentiment_score']:
            k[cf]['sentiment_score'].append(x)
        avss = (sum(k[cf]['sentiment_score']) /
                len(k[cf]['sentiment_score']))
        for x in sentiments[persons]['confidence']:
            k[cf]['confidence'].append(x)
        avcs = (sum(k[cf]['confidence']) / len(k[cf]['confidence']))
        k[cf]['avg_sentiment_score'] = avss
        k[cf]['avg_confidence'] = avcs
    else:
        am[fname].append({cf: sentiments[persons]})


def main(ff='./transcript_scores/'):
    toret = []
    # XXX: First go through the directory and get all the company names
    # that have been processed.
    onlyfiles = [f for f in listdir(ff) if isfile(join(ff, f))]
    onlyfiles.sort(reverse=True)      # sorted to make things faster
    # XXX: Get just the company name from the file
    companies = [c.split('_')[0] for c in onlyfiles]
    companies = list(set(companies))
    # XXX: Sort them alphabetically
    companies.sort(reverse=True)
    # XXX: Now start processing the files one after then another for CEO
    # and CFO information.

    for c in companies:
        print('Processing: ', c)
        no_matches = dict()
        all_matches = dict()
        # XXX: Get the ceo and cfo information for this company
        df = pd.read_csv('./ces_cfos/%s.csv' % c)
        for f in onlyfiles:
            fname = f.split('.')[0]
            fyear = fname.split('_')[-1]
            ceos = list(set(df[df['Year'] == int(fyear)]['CEO']))
            cfos = list(set(df[df['Year'] == int(fyear)]['CFO']))
            ceos_cfos = ceos + cfos
            if f.startswith(c):
                no_matches[fname] = list()
                all_matches[fname] = list()
                # XXX: Added who is CEO/CFO
                all_matches[fname].append({'CEO': ceos})
                all_matches[fname].append({'CFO': cfos})
                # XXX: Get the sentiment data
                with open(('%s%s' % (ff, f)), 'rb') as fd:
                    sentiments = json.load(fd)
                if sentiments == {}:
                    continue
                # XXX: Now start processing the CEO/CFO sentiments
                all_matches[fname].append({'date': sentiments['date']})
                no_matches[fname].append({'date': sentiments['date']})
                for cf in ceos_cfos:
                    cc = cf.split(' ')
                    # XXX: At least first and last name should be there
                    assert (len(cc) >= 2)
                    # XXX: Get all the keys that match
                    for persons in sentiments:
                        firstName = re.search(cc[0], persons, re.IGNORECASE)
                        lastName = re.search(cc[-1], persons, re.IGNORECASE)
                        # XXX: If the keys contain both, then we have
                        # found the CEO/CFO
                        if (firstName and lastName):
                            append_sentiments(all_matches, fname, cf, persons,
                                              sentiments)
                            # XXX: We found our guy!
                        elif lastName:
                            # XXX: We hope this is our guy!
                            append_sentiments(all_matches, fname, cf, persons,
                                              sentiments)
                        else:
                            # XXX: Just write the data to a file to
                            # check later on
                            no_matches[fname].append((persons +
                                                      '!='+cc[0] +
                                                      ' '+cc[-1]))
                        # XXX: Always append the date
            # print(no_matches)

        # XXX: Print all the mathces for all the files for a given
        # company
        with open('%s%s_processed.json' % ('./transcripts_processed/', c),
                  'w') as fd:
            json.dump(all_matches, fp=fd, indent=1)
        toret.append(c)
        # assert (False)
    return toret


def sentiment_plot():
    # XXX: Now we can print the timeseries of sentiment for CEO/CFO
    dir_to_process = './transcripts_processed/'
    df = pd.read_csv(dir_to_process+'comapnies.csv')
    for c in df['Companies']:
        f = dir_to_process+c+'_processed.json'
        # XXX: Plot the sentiment score as a time series
        with open(f, 'r') as fd:
            data = json.load(fd)
        # XXX: Now plot the damn time series
        quarters = [str(x) for x in list(data.keys())]
        # XXX: Sorted first by year then by quarters
        quarters.sort(key=lambda x: x.split('_')[-1]+'_'+x.split('_')[1])
        ceo_sentiment = [np.nan]*len(quarters)
        o_sentiment = [np.nan]*len(quarters)
        dates = [np.nan]*len(quarters)
        ceoname = list(np.nan)*len(quarters)
        cfoname = list(np.nan)*len(quarters)
        for i, q in enumerate(quarters):
            # XXX: There should be only 4 or less dictionary enteries in
            # each quarter.
            if len(data[q]) <= 2:
                continue

            # XXX: Process only if we have the data available
            ceo = data[q][0]['CEO'][0]
            ceoname[i] = ceo
            cfo = data[q][1]['CFO'][0]
            cfoname[i] = cfo
            dates[i] = pd.to_datetime(data[q][2]['date'])
            # XXX: Now get the ceo sentiment
            mceo = [x for x in data[q] if ceo in x.keys()]
            assert (len(mceo) <= 1)
            ceo_sentiment[i] = (mceo[0][ceo]['avg_sentiment_score']
                                if len(mceo) == 1 else np.nan)
            # XXX: Get the CFO/Other' sentiments
            mcfo = [x for x in data[q] if cfo in x.keys()]
            assert (len(mcfo) <= 1)
            o_sentiment[i] = (mcfo[0][cfo]['avg_sentiment_score']
                              if len(mcfo) == 1 else np.nan)
        # XXX: Make the data frame for plotting
        df = pd.DataFrame({'CEO': ceo_sentiment,
                           'CEO-Name': ceoname,
                           'Others': o_sentiment,
                           'Others-Name': cfoname,
                           'dates': dates})
        # df = df.dropna()
        print(df.info())


if __name__ == '__main__':
    companies = main()
    with open('./transcripts_processed/comapnies.csv', 'w') as fd:
        fd.write('Companies\n')
        for c in companies:
            fd.write(c+'\n')

    # XXX: Plot the sentiments
    # sentiment_plot()
