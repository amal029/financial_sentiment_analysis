#!/usr/bin/env python3

from bs4 import BeautifulSoup
import re
import json
from ollama import chat
from pydantic import BaseModel
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join


class Output(BaseModel):
    sentiment: float
    confidence: float
    reason: str


def get_sentiment(text, company_name, model=None):
    omodel = model
    if model is None:
        # XXX: This is just to avoid going over boundary
        model = "llama3.2"
    else:
        model = model
        ftext = r"You are an expert financial analyst. You will analyse \
        the financial data given to you. You will give a sentiment from \
        -1 to 1 for very negative to very positive for the data. \
        You will also give a confidence score from 0 to 1 indicating \
        how confident you are when giving the sentiment score. \
        You will give a reason for your sentiment score. \
        You will give the output in json format only."
    if omodel is not None:
        text = ftext + "data: " + text
        # XXX: First set the role of ollama

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
        mresponse.append(response['message']['content'])
    try:
        response = ''.join(mresponse)
        # print(response)
        # assert (False)
        res = json.loads(response)['sentiment']
        rc = json.loads(response)['confidence']
        reason = json.loads(response)['reason']
    except Exception:
        print('Exception occured: %s' % ' '.join(mresponse))
        res = 0
        rc = 0
        reason = ""
    # print('sentiment score: ', res, 'confidence: ', rc, 'reason:', reason,
    #       'company: ', company_name)
    return {'sentiment score': res, 'confidence': rc,
            'reason': reason, 'company_name': company_name}


def process(fName):
    soup = BeautifulSoup(ff, 'lxml')
    if (len(soup.get_text()) == 0):
        return None, None

    # XXX: Get the company name here
    span = re.search('COMPANY CONFORMED NAME:.*', soup.get_text()).span()
    company_name = soup.get_text()[span[0]:span[1]]

    # XXX: Get all the tables
    tables = soup.find_all('table')
    # XXX: Go through tables and get the rows
    to_print = False
    table_txts = list()
    for table in tables:
        s = list()
        for row in table.find_all('tr'):
            # XXX: For each of the row get the column
            prnline = False
            for c in row.find_all('td'):
                text = c.get_text().rstrip().strip()
                # XXX: Search for these words in the sentence
                if re.search('CONSOLIDATED +BALANCE +SHEETS', text,
                             re.IGNORECASE):
                    to_print = True
                if text.isascii() and text != '' and to_print:
                    s.append(text)
                    s.append(' ')
                    prnline = True
            if to_print and prnline:
                s.append('\n')
        if to_print:
            table_txts.append([''.join(s)])
    return table_txts, company_name


def get_sheets_only(tables):
    toret = list()
    for t in tables:
        t = t[0]
        if ((re.search('CURRENT ASSETS', t, re.IGNORECASE) or
             re.search('LIABILITIES:', t, re.IGNORECASE) or
             re.search('CASHFLOW', t, re.IGNORECASE))):
            toret.append(t)
    return ''.join(toret)


def process_file(ff, fname):
    res, company_name = process(ff)
    if res is None or company_name is None:
        return None
    print('Doing company: ', company_name)
    if res == '':
        print('Nothing obtained to perform sentiment analysis')
        return
    res = get_sheets_only(res)
    res = get_sentiment(res, company_name, model='llama3.2')
    with open('./10X_filing_sentiment/%s.json' % fname, 'w') as fd:
        fd.write(str(res))


if __name__ == '__main__':

    # XXX: Get the files that have already been processed
    mypath = './10X_filing_sentiment'
    donefiles = [f.split('.')[0]
                 for f in listdir(mypath) if isfile(join(mypath, f))]

    # XXX: Process the zipfile and then getting the sentiment
    with ZipFile('./10X_filings/10-X_2021.zip') as myzip:
        for i, f in enumerate(myzip.namelist()):
            if i >= 2:
                # XXX: Here if we are already done, then continue
                filename = f.split('/')[-1].split('.')[0]
                if filename in donefiles:
                    print('Skipping: ', filename, ' already done!')
                    continue
                with myzip.open(f) as myfile:
                    ff = myfile.read()
                    process_file(ff, filename)
                    # assert (False)
