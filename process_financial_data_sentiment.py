#!/usr/bin/env python
import pandas as pd
import tabulate as tb
import json
from pydantic import BaseModel
from ollama import chat
from os import listdir
from os.path import isfile, join


class Output(BaseModel):
    sentiment: float
    confidence: float
    reason: str


def get_sentiment(table, itable, tick=None, q=None, y1=None,
                  y2=None, filingdate=None, model=None):
    if model is None:
        model = "llama3.2"
    else:
        model = model

    ftext = (r"You are the best financial analyst. \
        You will analyse the balance sheet and income statement given to you.\
        The balance sheet and the income statement will be given as two \
        different tables.\ The first column of the balance sheet and\
        income statement gives details of the accounting items. \
        The second column of the balance sheet and income statement\
        will give the numbers for each row for quarter %s of\
        %s year. The third column will give the numbers for quarter %s \
        for %s year.\
        Analyse the balance sheet and income statement across the two\
        different quarters and years.\
        Use trend analysis and ratio analysis, from the balance sheet and, \
        Income statement to determine a sentiment score. \
        Give a sentiment score from -1 to 1.\
        A sentiment score of -1 indicates a very negative sentiment for \
        the company. A sentiment score of 1 indicates a very positive\
        sentiment. You will also give a confidence score from 0 to 1.\
        Confidence score of 0 means you have no confidence in your analysis.\
        A score of 1 indicates you have full confidence in your analysis.\
        Finally, you will give a detailed reason for you analysis.\
        Your reaoning should include the trend analysis and ratio analysis.\
        The output should be in json format only." % (q, y1, q, y2))

    if model is not None:
        text = ftext + '\n\nBalance sheet: \n\n' + table +\
            '\n\nIncome statement: \n\n' + itable
    # print(text)
    # assert (False)
    mresponse = list()
    for response in chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },], format=Output.model_json_schema(), keep_alive=0,
                         stream=True):
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


def getBalanceSheetData(model):
    # Get the files that are already done
    done_files = ['_'.join(f.split('_')[:3])
                  for f in listdir('./10X_filing_sentiment/')
                  if isfile(join('./10X_filing_sentiment/', f))]
    years = list(reversed(list(range(2010, 2025))))
    quarters = list(reversed(list(range(1, 5))))
    sp500 = pd.read_csv('sp500.csv')[['CIK', 'Symbol']]
    balance_mnemonics = pd.read_csv('./finance_mnemonics.csv')
    income_mnemonics = pd.read_csv('./income_statement_mnemonic.csv')
    income_description = list(income_mnemonics['Description'])
    # XXX: Read the csv from compustat
    data_cols = list(balance_mnemonics['mnemonic'])
    balance_data = data_cols[:-4]
    balance_data_desc = list(balance_mnemonics['Description'][:-4])
    data = pd.read_csv('./Quarter_financial_data.csv',
                       usecols=data_cols+list(income_mnemonics['mnemonic']))

    for (c, s) in zip(sp500['CIK'], sp500['Symbol']):
        # XXX: Now process the transcripts
        for y in years:
            for q in quarters:
                try:
                    # If it is already done then move on!
                    ff = '%s_Q%s_%s' % (s, q, y)
                    if ff in done_files:
                        print('Already done: %s' % ff)
                        continue
                    # Else process
                    print('Doing: %s' % ff)
                    pdata = data[(data['cik'] == c) &
                                 (data['fqtr'] == q) &
                                 ((data['fyearq'] == y) |
                                  (data['fyearq'] == y-1))]
                    # XXX: We now have the required balance sheet
                    # information
                    bdata = pdata[balance_data]
                    filingdate = list(bdata['datadate'])
                    fdata = pd.DataFrame({'': balance_data_desc[:-1],
                                          '%s_Q%s' % (y, q):
                                          bdata.iloc[1, :-1],
                                          '%s_Q%s' % (y-1, q):
                                          bdata.iloc[0, :-1]},
                                         index=balance_data[:-1]).dropna()
                    # XXX: Read the income statement data
                    idata = pdata[income_mnemonics['mnemonic']]
                    itable = pd.DataFrame({'': income_description,
                                           '%s_Q%s' % (y, q):
                                           idata.iloc[1, :],
                                           '%s_Q%s' % (y-1, q):
                                           idata.iloc[0, :]},
                                          index=list(
                                              income_mnemonics['mnemonic'])
                                          ).dropna()

                    # XXX: Tabulate the data
                    headers = ['Account Items', '%s_Q%s' % (y, q),
                               '%s_Q%s' % (y-1, q)]
                    ftable = tb.tabulate(fdata, headers=headers,
                                         showindex='never')
                    itablet = tb.tabulate(itable, headers=headers,
                                          showindex='never')
                    ret = get_sentiment(ftable, itablet,
                                        tick=s, q=q, y1=y, y2=y-1,
                                        filingdate=filingdate, model=model)
                    with open('./10X_filing_sentiment/%s_Q%s_%s_%s.json' %
                              (s, q, y, model), 'w') as fd:
                        json.dump(ret, fd)
                        # fdata.to_csv(
                        #     './10X_filing_sentiment/%s_Q%s_%s_%s_balance.csv'
                        #     % (s, q, y, model))
                        # itable.to_csv(
                        #     './10X_filing_sentiment/%s_Q%s_%s_%s_income.csv'
                        #     % (s, q, y, model))
                except Exception:
                    pass


if __name__ == '__main__':
    for model in ['gemma3:12b']:
        getBalanceSheetData(model=model)
