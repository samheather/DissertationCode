from random import randint

def getDandelionId():
    ids = [
            {'id':'69be7007','key':'96359009ccf992ef98268734570b0d7f'},
            #{'id':'d37adf4c','key':'3dccf99ae339254afbb8b642cf719131'},
            {'id':'464ee865','key':'c5f83188fa1cf13448ead66bb01ee56e'},
            {'id':'6f81f9da','key':'870bdff36db2fa363de4b05be1bcc2d5'}
        ]
    index = randint(0,len(ids)-1)
    return ids[index]