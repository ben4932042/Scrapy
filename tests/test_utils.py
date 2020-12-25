from dependencies import get_hash256
from dependencies import replace_word
from dependencies import judge_skip_word
import pytest

class TestUtils:
    def test_get_hash256(self):
        assert get_hash256("1") == get_hash256("1")

    def test_replace_word(self):
        assert replace_word("\t") == '。' 
        assert replace_word("\n") == '。' 
        assert replace_word("\r") == '。'
        assert replace_word("\xa0") == '。'
        assert replace_word("<br>") == '。'
        assert replace_word("<br/>") == '。' 
        assert replace_word("test") == 'test'
        

    def test_judge_skip_word(self):
        __test_skip_word_list = ['adbert', '123']
        assert judge_skip_word('adbert', __test_skip_word_list) == 1
        assert judge_skip_word('adber', __test_skip_word_list) == 0
        assert judge_skip_word('123', __test_skip_word_list) == 1
