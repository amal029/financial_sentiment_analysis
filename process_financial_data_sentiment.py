#!/usr/bin/env python
import pandas as pd
import tabulate as tb
import json
from pydantic import BaseModel
from ollama import chat


class Output(BaseModel):
    sentiment: float
    confidence: float
    reason: str


def get_sentiment(table, tick=None, q=None, y1=None,
                  y2=None, filingdate=None, model=None):
    if model is None:
        model = "llama3.2"
    else:
        model = model

    ftext = (r"You are a financial analyst. \
        You will analyse the balance sheet given to you.\
        The balance sheet will be given as a table.\
        The first column of the balance sheet gives details \
        of the accounting items. The second column will give the numbers\
        for each row for quarter %s of\
        %s year. The third column will give the numbers for quarter %s \
        quarter from %s year.\
        Analyse the balance sheet across the two different quarters and years.\
        You will give a sentiment score for the company, after \
        analysing the balance sheet, from -1 to 1.\
        A sentiment score of -1 indicates a very negative sentiment.\
        A sentiment score of 1 indicates a very positive sentiment.\
        You will also give a confidence score from 0 to 1.\
        Confidence score of 0 means you have no confidence in your analysis.\
        A score of 1 indicates you have full confidence in your analysis.\
        Finally, you will give a detailed reason for you analysis.\
        The output should be in json format only." % (q, y1, q, y2))

    if model is not None:
        text = ftext + '\n\n' + table
    mresponse = list()
    for response in chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },], format=Output.model_json_schema(), stream=True):
        mresponse.append(response['message']['content'])
    try:
        response = ''.join(mresponse)
        # print('response:', response)
        res = json.loads(response)['sentiment']
        rc = json.loads(response)['confidence']
        reason = json.loads(response)['reason']
    except Exception:
        print('Exception occured: %s' % ' '.join(mresponse))
        res = 0
        rc = 0
        reason = ''

    # print('sentiment score: ', res, 'confidence: ', rc, 'reason: ', reason,
    #       'filingdate: ', filingdate)

    return {'sentiment_score': res,
            'confidence': rc,
            'reason': reason,
            'ticker': tick,
            'filingdate': filingdate}


def getBalanceSheetData():
    years = list(reversed(list(range(2010, 2025))))
    quarters = list(reversed(list(range(1, 5))))
    sp500 = pd.read_csv('sp500.csv')[['CIK', 'Symbol']]
    balance_mnemonics = pd.read_csv('./finance_mnemonics.csv')
    # XXX: Read the csv from compustat
    data_cols = list(balance_mnemonics['mnemonic'])
    balance_data = data_cols[:-4]
    balance_data_desc = list(balance_mnemonics['Description'][:-4])
    data = pd.read_csv('./Quarter_financial_data.csv', usecols=data_cols)

    for (c, s) in zip(sp500['CIK'], sp500['Symbol']):
        # XXX: Now process the transcripts
        for y in years:
            for q in quarters:
                try:
                    print('Doing: ', s, 'Q', q, y)
                    pdata = data[(data['cik'] == c) &
                                 (data['fqtr'] == q) &
                                 ((data['fyearq'] == y) |
                                  (data['fyearq'] == y-1))]
                    # XXX: We now have the required balance sheet
                    # information
                    pdata = pdata[balance_data]
                    filingdate = list(pdata['datadate'])
                    fdata = pd.DataFrame({'': balance_data_desc[:-1],
                                          '%s_Q%s' % (y, q):
                                          pdata.iloc[1, :-1],
                                          '%s_Q%s' % (y-1, q):
                                          pdata.iloc[0, :-1]},
                                         index=balance_data[:-1]).dropna()
                    # XXX: Tabulate the data
                    headers = ['Account Items', '%s_Q%s' % (y, q),
                               '%s_Q%s' % (y-1, q)]
                    ftable = tb.tabulate(fdata, headers=headers,
                                         showindex='never')
                    ret = get_sentiment(ftable, tick=s, q=q, y1=y, y2=y-1,
                                        filingdate=filingdate)
                    with open('./10X_filing_sentiment/%s_Q%s_%s.json' %
                              (s, q, y), 'w') as fd:
                        json.dump(ret, fd)
                        fdata.to_csv('./10X_filing_sentiment/%s_Q%s_%s.csv' %
                                     (s, q, y))
                except Exception:
                    pass


if __name__ == '__main__':
    getBalanceSheetData()
