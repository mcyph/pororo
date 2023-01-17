# -*- coding: utf-8 -*-
import json
from typing import Dict
from urllib.parse import urlencode
from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def get_request(endpoint: str, params: Dict[str, str]):
    return client.get(endpoint+"?"+urlencode(params))


def _(o):
    return json.loads(json.dumps(o))


#===========================================================#
# Sequence Tagging
#===========================================================#


def test_dependency_parse():
    response = get_request("/dependencyParse", {'sentences': "분위기도 좋고 음식도 맛있었어요. 한 시간 기다렸어요."})
    assert response.status_code == 200
    assert response.json() == [[1, '분위기도', 2, 'NP_SBJ'], [2, '좋고', 4, 'VP'], [3, '음식도', 4, 'NP_SBJ'], [4, '맛있었어요.', 7, 'VP'], [5, '한', 6, 'DP'], [6, '시간', 7, 'NP_OBJ'], [7, '기다렸어요.', -1, 'VP']]

    response = get_request("/dependencyParse", {'sentences': "한시간 기다렸어요."})
    assert response.status_code == 200
    assert response.json() == [[1, '한시간', 2, 'NP_OBJ'], [2, '기다렸어요.', -1, 'VP']]

    response = get_request("/dependencyParse", {'sentences': "한시간 기다렸어요."})
    assert response.status_code == 200
    assert response.json() == [[1, '한시간', 2, 'NP_OBJ'], [2, '기다렸어요.', -1, 'VP']]


def test_named_entity_recognition():
    response = get_request("/namedEntityRecognition", {'iso': 'en', 'sentences': "It was in midfield where Arsenal took control of the game, and that was mainly down to Thomas Partey and Mohamed Elneny."})
    assert response.status_code == 200
    assert response.json() == _([('It', 'O'), ('was', 'O'), ('in', 'O'), ('midfield', 'O'), ('where', 'O'), ('Arsenal', 'ORG'), ('took', 'O'), ('control', 'O'), ('of', 'O'), 
    ('the', 'O'), ('game', 'O'), (',', 'O'), ('and', 'O'), ('that', 'O'), ('was', 'O'), ('mainly', 'O'), ('down', 'O'), ('to', 'O'), ('Thomas Partey', 'PERSON'), ('and', 'O'), 
    ('Mohamed Elneny', 'PERSON'), ('.', 'O')])

    #response = get_request("/namedEntityRecognition", {'iso': 'ko', 'sentences': "손흥민은 28세의 183 센티미터, 77 킬로그램이며, 현재 주급은 약 3억 원이다."})
    #assert response.status_code == 200
    #assert response.json() == _([('손흥민', 'PERSON'), ('은', 'O'), (' ', 'O'), ('28세', 'QUANTITY'), ('의', 'O'), (' ', 'O'), ('183 센티미터', 'QUANTITY'), (',', 'O'), (' ', 'O'), ('77 킬로그램', 'QUANTITY'), ('이며,', 'O'), (' ', 'O'), ('현재', 'O'), (' ', 'O'), ('주급은', 'O'), (' ', 'O'), ('약 3억 원', 'QUANTITY'), ('이다.', 'O')]
    # )
    response = get_request("/namedEntityRecognition", {'iso': 'ko', 'sentences': "손흥민은 28세의 183 센티미터, 77 킬로그램이며, 현재 주급은 약 3억 원이다."})
    assert response.status_code == 200
    assert response.json() == _([('손흥민', 'PERSON'), ('은', 'O'), (' ', 'O'), ('28세', 'AGE'), ('의', 'O'), (' ', 'O'), ('183 센티미터', 'LENGTH/DISTANCE'), (',', 'O'), (' ', 'O'), 
    ('77 킬로그램', 'WEIGHT'), ('이며,', 'O'), (' ', 'O'), ('현재', 'O'), (' ', 'O'), ('주급은', 'O'), (' ', 'O'), ('약 3억 원', 'MONEY'), ('이다.', 'O')])

    # NER for chinese+japanese uses a lot of memory
    response = get_request("/namedEntityRecognition", {'iso': 'zh', 'sentences': "毛泽东（1893年12月26日－1976年9月9日），字润之，湖南湘潭人。中华民国大陆时期、中国共产党和中华人民共和国的重要政治家、经济家、军事家、战略家、外交家和诗人。"})
    assert response.status_code == 200
    assert response.json() == _([('毛泽东', 'PERSON'), ('（', 'O'), ('1893年12月26日－1976年9月9日', 'DATE'), ('）', 'O'), ('，', 'O'), ('字润之', 'O'), ('，', 'O'), ('湖南', 'GPE'), 
    ('湘潭', 'GPE'), ('人', 'O'), ('。', 'O'), ('中华民国大陆时期', 'GPE'), ('、', 'O'), ('中国共产党', 'ORG'), ('和', 'O'), ('中华人民共和国', 'GPE'), ('的', 'O'), ('重', 'O'), 
    ('要', 'O'), ('政', 'O'), ('治', 'O'), ('家', 'O'), ('、', 'O'), ('经', 'O'), ('济', 'O'), ('家', 'O'), ('、', 'O'), ('军', 'O'), ('事', 'O'), ('家', 'O'), ('、', 'O'), 
    ('战', 'O'), ('略', 'O'), ('家', 'O'), ('、', 'O'), ('外', 'O'), ('交', 'O'), ('家', 'O'), ('和', 'O'), ('诗', 'O'), ('人', 'O'), ('。', 'O')])

    response = get_request("/namedEntityRecognition", {'iso': 'ja', 'sentences': "豊臣 秀吉、または羽柴 秀吉は、戦国時代から安土桃山時代にかけての武将、大名。天下人、武家関白、太閤。三英傑の一人。"})
    assert response.status_code == 200
    assert response.json() == _([('豊臣秀吉', 'PERSON'), ('、', 'O'), ('または', 'O'), ('羽柴秀吉', 'PERSON'), ('は', 'O'), ('、', 'O'), ('戦国時代', 'DATE'), ('から', 'O'), 
    ('安土桃山時代', 'DATE'), ('にかけて', 'O'), ('の', 'O'), ('武将', 'O'), ('、', 'O'), ('大名', 'O'), ('。', 'O'), ('天下', 'O'), ('人', 'O'), ('、', 'O'), ('武家', 'O'), 
    ('関白', 'O'), ('、太閤', 'O'), ('。', 'O'), ('三', 'O'), ('英', 'O'), ('傑', 'O'), ('の', 'O'), ('一', 'O'), ('人', 'O'), ('。', 'O')])


def test_part_of_speech():
    response = get_request("/partOfSpeech", {'iso': 'ko', 'sentences': "안녕하세요. 제 이름은 카터입니다."})
    assert response.status_code == 200
    assert response.json() == _([('안녕', 'NNG'), ('하', 'XSV'), ('시', 'EP'), ('어요', 'EF'), ('.', 'SF'), (' ', 'SPACE'),
    ('저', 'NP'), ('의', 'JKG'), (' ', 'SPACE'), ('이름', 'NNG'), ('은', 'JX'), (' ', 'SPACE'),
    ('카터', 'NNP'), ('이', 'VCP'), ('ᄇ니다', 'EF'), ('.', 'SF')])

    response = get_request("/partOfSpeech", {'iso': 'ja', 'sentences': "日本語でペラペラではないです"})
    assert response.status_code == 200
    assert response.json() == _([('日本語', '名詞'), ('で', '助詞'), ('ペラペラ', '副詞'), ('で', '助動詞'),
    ('は', '助詞'), ('ない', '助動詞'), ('です', '助動詞')])

    response = get_request("/partOfSpeech", {'iso': 'en', 'sentences': "The striped bats are hanging, on their feet for best."})
    assert response.status_code == 200
    assert response.json() == _([('The', 'DT'), (' ', 'SPACE'), ('striped', 'JJ'), (' ', 'SPACE'), ('bats', 'NNS'),
    (' ', 'SPACE'), ('are', 'VBP'), (' ', 'SPACE'), ('hanging', 'VBG'), (',', ','),
    (' ', 'SPACE'), ('on', 'IN'), (' ', 'SPACE'), ('their', 'PRP$'), (' ', 'SPACE'),
    ('feet', 'NNS'), (' ', 'SPACE'), ('for', 'IN'), (' ', 'SPACE'), ('best', 'JJS'), ('.', '.')])
    
    response = get_request("/partOfSpeech", {'iso': 'zh', 'sentences': "乒乓球拍卖完了"})
    assert response.status_code == 200
    assert response.json() == _([('乒乓球', 'n'), ('拍卖', 'v'), ('完', 'v'), ('了', 'ul')])


def test_sentiment_analysis():
    # Korean needs a lot of memory
    response = get_request("/sentimentAnalysis", {'iso': 'ko', 'sentences': "배송이 버트 학습시키는 것 만큼 느리네요"})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Negative'
    #assert 'negative' in response.json()
    #assert 'positive' in response.json()

    response = get_request("/sentimentAnalysis", {'iso': 'ko', 'sentences': "배송이 경량화되었는지 빠르네요"})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Positive'

    response = get_request("/sentimentAnalysis", {'iso': 'ko', 'sentences': "꽤 맘에 들었어요. 겉에서 봤을땐 허름?했는데 맛도 있고, 괜찮아요"})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Positive'

    response = get_request("/sentimentAnalysis", {'iso': 'ko', 'sentences': "예약하고 가세요 대기줄이 깁니다 훠궈는 하이디라오가 비싼만큼 만족도가 제일 높아요"})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Negative'

    response = get_request("/sentimentAnalysis", {'iso': 'ja', 'sentences': "日が暑くもイライラか。"})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Negative'

    response = get_request("/sentimentAnalysis", {'iso': 'ja', 'sentences': '日が良く散歩に行きたいです。'})
    assert response.status_code == 200
    assert response.json()#['overall'] == 'Positive'


#===========================================================#
# Text Classification
#===========================================================#


def test_zero_shot_topic_classification():
    # English appears to need a lot of memory
    response = get_request("/zeroShotTopicClassification", {'iso': 'en', 'sentences': "Who are you voting for in 2020?"})
    assert response.status_code == 200
    assert response.json() == ["business", "art & culture", "politics"]
    
    response = get_request("/zeroShotTopicClassification", {'iso': 'ko', 'sentences': '''라리가 사무국, 메시 아닌 바르사 지지..."바이 아웃 유효" [공식발표]'''})
    assert response.status_code == 200
    assert response.json() == ["스포츠", "사회", "정치", "경제", "생활/문화", "IT/과학"]
    
    response = get_request("/zeroShotTopicClassification", {'iso': 'ko', 'sentences': '''장제원, 김종인 당무감사 추진에 “참 잔인들 하다”···정강정책 개정안은 “졸작”'''})
    assert response.status_code == 200
    assert response.json() == ["스포츠", "사회", "정치", "경제", "생활/문화", "IT/과학"]
    
    response = get_request("/zeroShotTopicClassification", {'iso': 'ja', 'sentences': "香川 真司は、兵庫県神戸市垂水区出身のプロサッカー選手。元日本代表。ポジションはMF、FW。ボルシア・ドルトムント時代の2010-11シーズンでリーグ前半期17試合で8得点を記録し9シーズンぶりのリーグ優勝に貢献。キッカー誌が選定したブンデスリーガの年間ベスト イレブンに名を連ねた。"})
    assert response.status_code == 200
    assert response.json() == ["スポーツ", "政治", "技術"]
    
    response = get_request("/zeroShotTopicClassification", {'iso': 'zh', 'sentences': "商务部14日发布数据显示，今年前10个月，我国累计对外投资904.6亿美元，同比增长5.9%。"})
    assert response.status_code == 200
    assert response.json() == ["政治", "经济", "国际化"]


def test_natural_language_inference():
    response = get_request("/naturalLanguageInference", {'iso': 'ko', 'sentence_1': "저는, 그냥 알아내려고 거기 있었어요", 'sentence_2': "나는 처음부터 그것을 잘 이해했다"})
    assert response.status_code == 200
    assert response.json() == 'Contradiction'
    
    response = get_request("/naturalLanguageInference", {'iso': 'ja', 'sentence_1': '古い紳士は、洗濯をしながら写真を撮っていることがユーモラスであることがわかります。', 'sentence_2': '洗濯をしながら男が笑う'})
    assert response.status_code == 200
    assert response.json() == 'Entailment'
    
    response = get_request("/naturalLanguageInference", {'iso': 'zh', 'sentence_1': '一群人抬头看着建筑物屋顶边缘的3人。', 'sentence_2': '三人正在楼梯上爬下来。'})
    assert response.status_code == 200
    assert response.json() == 'Contradiction'
    
    response = get_request("/naturalLanguageInference", {'iso': 'en', 'sentence_1': "A soccer game with multiple males playing.", 'sentence_2': "Some men are playing a sport."})
    assert response.status_code == 200
    assert response.json() == 'Entailment'


#===========================================================#
# Seq2Seq
#===========================================================#


def test_grapheme_to_phoneme():
    response = get_request("/graphemeToPhoneme", {'iso': 'ko', 'sentences': "어제는 날씨가 맑았는데, 오늘은 흐리다."})
    assert response.status_code == 200
    assert response.json() == _([('어제는', '어제는'), ('날씨가', '날씨가'), ('맑았는데,', '말간는데,'), ('오늘은', '오느른'), ('흐리다.', '흐리다.')])

    response = get_request("/graphemeToPhoneme", {'iso': 'en', 'sentences': "I have $250 in my pocket."})
    assert response.status_code == 200
    assert response.json() == ['AY1', ' ', 'HH', 'AE1', 'V', ' ', 'T', 'UW1', ' ', 'HH', 'AH1', 'N', 'D', 'R', 'AH0', 'D', ' ', 'F', 'IH1', 'F', 'T', 'IY0', ' ', 
    'D', 'AA1', 'L', 'ER0', 'Z', ' ', 'IH0', 'N', ' ', 'M', 'AY1', ' ', 'P', 'AA1', 'K', 'AH0', 'T', ' ', '.']

    #response = get_request("/graphemeToPhoneme", {'iso': 'zh', 'sentences': "然而，他红了20年以后，他竟退出了大家的视线。"})
    #assert response.status_code == 200
    #assert response.json() == _([('然', 'ran2'), ('而', 'er2'), (',', ','), ('他', 'ta1'), ('红', 'hong2'), ('了', 'le5'), ('2', '2'), ('0', '0'), ('年', 'nian2'), ...])

    response = get_request("/graphemeToPhoneme", {'iso': 'ja', 'sentences': "pythonが大好きです"})
    assert response.status_code == 200
    assert response.json() == _([('python', 'python'), ('が', 'ga'), ('大好き', 'daisuki'), ('です', 'desu')])


#===========================================================#
# Miscellaneous
#===========================================================#


async def test_morphological_inflection():
    response = get_request("/morphologicalInflection", {'iso': 'ko', 'word': "곱"})
    assert response.status_code == 200
    assert response.json() #== _([['Action Verb', [('거나', '곱거나'), ('거늘', '곱거늘'), ('거니', '곱거니') ...]]])
    
    response = get_request("/morphologicalInflection", {'iso': 'en', 'word': "love"})
    assert response.status_code == 200
    assert response.json() == _({'NN': [('loves', 'NNS')], 'VB': [('loves', 'VBZ'), ('loved', 'VBD'), ('loved', 'VBN'), ('loving', 'VBG')]})
    
    response = get_request("/morphologicalInflection", {'iso': 'ja', 'word': "あえぐ"})
    assert response.status_code == 200
    assert response.json() == _({'verb': [('あえが', '未然形'), ('あえご', '未然ウ接続'), ('あえぎ', '連用形'), ('あえい', '連用タ接続'), ('あえげ', '仮定形'), ('あえげ', '命令ｅ'), ('あえぎゃ', '仮定縮約１')]})    


"""
async def test_ocr():
    ocr = Pororo(task="ocr", lang="ko")
    ocr(IMAGE_PATH)
    ["사이렌'(' 신마'", "내가 말했잖아 속지열라고 이 손을 잡는 너는 위협해질 거라고"]

    ocr = Pororo(task="ocr", lang="ko")
    ocr(IMAGE_PATH, detail=True)
    {
        'description': ["사이렌'(' 신마', "내가 말했잖아 속지열라고 이 손을 잡는 너는 위협해질 거라고"],
        'bounding_poly': [
            {
                'description': "사이렌'(' 신마'",
                'vertices': [
                    {'x': 93, 'y': 7},
                    {'x': 164, 'y': 7},
                    {'x': 164, 'y': 21},
                    {'x': 93, 'y': 21}
                ]
            },
            {
                'description': "내가 말했잖아 속지열라고 이 손을 잡는 너는 위협해질 거라고",
                'vertices': [
                    {'x': 0, 'y': 30},
                    {'x': 259, 'y': 30},
                    {'x': 259, 'y': 194},
                    {'x': 0, 'y': 194}]}
                ]
            }
    }
"""


async def test_collocation():
    response = get_request("/collocation", {'iso': 'ko', 'word': "먹"})
    assert response.status_code == 200
    assert response.json()# == _()
    
    response = get_request("/collocation", {'iso': 'ja', 'word': "東京"})
    assert response.status_code == 200
    assert response.json() == _({'noun': {'noun': [('都', 137), ('家', 21), ('年', 18), ('府', 17), ('市', 12), ('式', 12), ('デザイナー', 10), ('日', 10), ('都立', 9), ('県', 9), ('出身', 8), ('証券', 8), ('後', 6)]}})
    
    response = get_request("/collocation", {'iso': 'en', 'word': "george"})
    assert response.status_code == 200
    assert response.json() == _({'noun': {'noun': [('washington', 13), ('gen.', 7)]}})
    
    response = get_request("/collocation", {'iso': 'zh', 'word': "世界杯"})
    assert response.status_code == 200
    assert response.json()# == _({'noun': {'noun': [('2002年', 72), ('足球赛', 71), ('冠军', 53), ('2006年', 39), ('決賽', 35), ('决赛', 30), ('1998年', 26), ('外圍賽', 25), ('2010年', 23), ('2018年', 22), ('冠軍', 21), ...}})
    
