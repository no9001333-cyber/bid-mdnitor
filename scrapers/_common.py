"""
scrapers 공통 유틸리티
- 투찰마감이 설정된 기간(MIN~MAX일) 안에 있는 공고만 통과시키는 함수
"""

import re
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MIN_DAYS_UNTIL_DEADLINE, MAX_DAYS_UNTIL_DEADLINE

import time
import requests


def get_with_retry(url, params=None, headers=None, timeout=30, retries=2, backoff=3):
    """일시적인 타임아웃/연결 오류에 대비해 몇 번 재시도하는 GET 요청."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(backoff)
    raise last_error


def parse_deadline(deadline_text: str):
    """'2026-08-11 12:00', '20260811 1200' 등 다양한 형식에서 날짜만 뽑아 datetime으로 변환.
    파싱 실패 시 None 반환."""
    if not deadline_text:
        return None
    m = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", str(deadline_text))
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def is_deadline_in_range(deadline_text: str) -> bool:
    """투찰마감까지 남은 일수가 MIN_DAYS_UNTIL_DEADLINE ~ MAX_DAYS_UNTIL_DEADLINE 사이인지 확인.
    마감일을 파싱할 수 없으면 일단 통과시킴 (걸러내지 않음)."""
    d = parse_deadline(deadline_text)
    if d is None:
        return True
    days_left = (d - datetime.now()).days
    return MIN_DAYS_UNTIL_DEADLINE <= days_left <= MAX_DAYS_UNTIL_DEADLINE
