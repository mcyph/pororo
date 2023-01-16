from pororo import Pororo
from fastapi import FastAPI


app = FastAPI()
MAXIMUM_CACHE_SIZE = 10


class LRUCache:
    def __init__(self, capacity):
        # From https://www.kunxi.org/2014/05/lru-cache-in-python/
        self.capacity = capacity
        self.tm = 0
        self.cache = {}
        self.lru = {}

    def __getitem__(self, key):
        if key in self.cache:
            self.lru[key] = self.tm
            self.tm += 1
            return self.cache[key]
        return -1

    def __setitem__(self, key, value):
        if len(self.cache) >= self.capacity:
            # find the LRU entry
            old_key = min(self.lru.keys(), key=lambda k:self.lru[k])
            self.cache.pop(old_key)
            self.lru.pop(old_key)
        self.cache[key] = value
        self.lru[key] = self.tm
        self.tm += 1


_cache = LRUCache(capacity=MAXIMUM_CACHE_SIZE)


class CachingDict:
    def __init__(self, unique_key: str, backing_dict: dict):
        self.__unique_key = unique_key
        self.__backing_dict = backing_dict
    
    def __getitem__(self, item):
        if (self.__unique_key, item) not in _cache:
            print("Creating key:", self.__unique_key, item)
            _cache[self.__unique_key, item] = self.__backing_dict[item]()
        return _cache[self.__unique_key, item]


#===========================================================#
# Sequence Tagging
#===========================================================#


dp = Pororo(task="dep_parse", lang="ko")
pos = CachingDict('pos', {
    'ko': lambda: Pororo(task="pos", lang="ko"),
    'ja': lambda: Pororo(task="pos", lang="ja"),
    'en': lambda: Pororo(task="pos", lang="en"),
    'zh': lambda: Pororo(task="pos", lang="zh"),
})
ner = CachingDict('ner', {
    'en': lambda: Pororo(task="ner", lang="en"),
    'ko': lambda: Pororo(task="ner", lang="ko"),
    'zh': lambda: Pororo(task="ner", lang="zh"),
    'ja': lambda: Pororo(task="ner", lang="ja"),
})
sa = CachingDict('sa', {
    'ja': lambda: {
        "Internal Data": Pororo(task="sentiment", lang="ja")
    },
    'ko': lambda: {
        "Shopping Reviews": Pororo(task="sentiment", model="brainbert.base.ko.nsmc", lang="ko"),
        "Movie Reviews": Pororo(task="sentiment", model="brainbert.base.ko.shopping", lang="ko"),
    }
})


@app.get("/dependencyParse")
async def _(sentences: str):
    return dp(sentences)


@app.get("/namedEntityRecognition")
async def _(iso: str, sentences: str):
    if iso == 'ko':
        # Can't imagine a situation where word sense disambiguation wouldn't 
        # be preferred if it's available for Korean - always enable
        return ner[iso](sentences, apply_wsd=True)
    return ner[iso](sentences)


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


zsl = CachingDict('zsl', {
    'en': lambda: Pororo(task="zero-topic"),
    'ko': lambda: Pororo(task="zero-topic", lang="ko"),
    'ja': lambda: Pororo(task="zero-topic", lang="ja"),
    'zh': lambda: Pororo(task="zero-topic", lang="zh"),
})
nli = CachingDict('nli', {
    'ko': lambda: Pororo(task="nli", lang="ko"),
    'ja': lambda: Pororo(task="nli", lang="ja"),
    'zh': lambda: Pororo(task="nli", lang="zh"),
    'en': lambda: Pororo(task="nli", lang="en"),
})

@app.get("/zeroShotTopicClassification")
async def _(iso: str, sentences: str):
    return zsl[iso](sentences)


@app.get("/naturalLanguageInference")
async def _(iso: str, sentences: str):
    return nli[iso](sentences)


#===========================================================#
# Seq2Seq
#===========================================================#


g2p = CachingDict('g2p', {
    'ko': lambda: Pororo(task="g2p", lang="ko"),
    'en': lambda: Pororo(task="g2p", lang="en"),
    'zh': lambda: Pororo(task="g2p", lang="zh"),
    'ja': lambda: Pororo(task="g2p", lang="ja"),
})


@app.get("/graphemeToPhoneme")
async def _(iso: str, sentences: str):
    return g2p[iso](sentences, align=True)


#===========================================================#
# Miscellaneous
#===========================================================#


inflection = CachingDict('inflection', {
    'ko': lambda: Pororo(task="inflection", lang="ko"),
    'en': lambda: Pororo(task="inflection", lang="en"),
    'ja': lambda: Pororo(task="inflection", lang="ja"),
})
ocr = Pororo(task="ocr", lang="ko")
col = CachingDict('col', {
    'ko': lambda: Pororo(task="col", lang="ko"),
    'ja': lambda: Pororo(task="collocation", lang="ja"),
    'en': lambda: Pororo(task="col", lang="en"),
    'zh': lambda: Pororo(task="col", lang="zh"),
})

@app.get("/morphologicalInflection")
async def _(iso: str, word: str):
    return inflection[iso](word)


@app.get("/ocr")
async def _(image_data: str):
    return ocr(image_data, detail=True)


@app.get("/collocation")
async def _(iso: str, word: str):
    return col[iso](word, detail=True)

