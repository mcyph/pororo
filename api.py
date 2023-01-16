from pororo import Pororo
from fastapi import FastAPI


app = FastAPI()


#===========================================================#
# Sequence Tagging
#===========================================================#


dp = Pororo(task="dep_parse", lang="ko")
pos = {
    'ko': Pororo(task="pos", lang="ko"),
    'ja': Pororo(task="pos", lang="ja"),
    'en': Pororo(task="pos", lang="en"),
    'zh': Pororo(task="pos", lang="zh"),
}
ner = {
    'en': Pororo(task="ner", lang="en"),
    'ko': Pororo(task="ner", lang="ko"),
    'zh': Pororo(task="ner", lang="zh"),
    'ja': Pororo(task="ner", lang="ja"),
}
sa = {
    'ja': {
        "Internal Data": Pororo(task="sentiment", lang="ja")
    },
    'ko': {
        "Shopping Reviews": Pororo(task="sentiment", model="brainbert.base.ko.nsmc", lang="ko"),
        "Movie Reviews": Pororo(task="sentiment", model="brainbert.base.ko.shopping", lang="ko"),
    }
}


@app.get("/dependencyParse")
async def _(sentences: str):
    return dp(sentences)


#@app.get("/namedEntityRecognition")
#async def _(iso: str, sentences: str):
#    if iso == 'ko':
#        # Can't imagine a situation where word sense disambiguation wouldn't 
#        # be preferred if it's available for Korean - always enable
#        return ner[iso](sentences, apply_wsd=True)
#    return ner[iso](sentences)


@app.get("/partOfSpeech")
async def _(iso: str, sentences: str):
    return pos[iso](sentences)


@app.get("/sentimentAnalysis")
async def _(iso: str, sentences: str):
    r = sa[iso](sentences, probabilities=True)
    for k, v in r.items():
        v['overall'] = 'Positive' if v['positive'] >= 0.5 else 'Negative'
    return r


#===========================================================#
# Text Classification
#===========================================================#


#zsl = {
#    'en': Pororo(task="zero-topic"),
#    'ko': Pororo(task="zero-topic", lang="ko"),
#    'ja': Pororo(task="zero-topic", lang="ja"),
#    'zh': Pororo(task="zero-topic", lang="zh"),
#}
#nli = {
#    'ko': Pororo(task="nli", lang="ko"),
#    'ja': Pororo(task="nli", lang="ja"),
#    'zh': Pororo(task="nli", lang="zh"),
#    'en': Pororo(task="nli", lang="en"),
#}

#@app.get("/zeroShotTopicClassification")
#async def _(iso: str, sentences: str):
#    return zsl[iso](sentences)


#@app.get("/naturalLanguageInference")
#async def _(iso: str, sentences: str):
#    return nli[iso](sentences)


#===========================================================#
# Seq2Seq
#===========================================================#


g2p = {
    'ko': Pororo(task="g2p", lang="ko"),
    'en': Pororo(task="g2p", lang="en"),
    'zh': Pororo(task="g2p", lang="zh"),
    'ja': Pororo(task="g2p", lang="ja"),
}


@app.get("/graphemeToPhoneme")
async def _(iso: str, sentences: str):
    return g2p[iso](sentences, align=True)


#===========================================================#
# Miscellaneous
#===========================================================#


inflection = {
    'ko': Pororo(task="inflection", lang="ko"),
    'en': Pororo(task="inflection", lang="en"),
    'ja': Pororo(task="inflection", lang="ja"),
}
ocr = Pororo(task="ocr", lang="ko")
col = {
    'ko': Pororo(task="col", lang="ko"),
    'ja': Pororo(task="collocation", lang="ja"),
    'en': Pororo(task="col", lang="en"),
    'zh': Pororo(task="col", lang="zh"),
}

@app.get("/morphologicalInflection")
async def _(iso: str, word: str):
    return inflection[iso](word)


@app.get("/ocr")
async def _(image_data: str):
    return ocr(image_data, detail=True)


@app.get("/collocation")
async def _(iso: str, word: str):
    return col[iso](word, detail=True)


