"""
한국토지주택공사(LH) 입찰공고 수집기
공공데이터포털의 "한국토지주택공사 입찰공고정보" OpenAPI 사용
(이 API는 XML만 응답합니다 - JSON 파라미터를 줘도 무시되므로 XML로 파싱합니다)
 
사전 준비:
1) https://www.data.go.kr 에서 "한국토지주택공사 입찰공고정보" 검색 → 활용신청 (자동승인)
2) 발급받은 서비스키를 환경변수 LH_SERVICE_KEY 로 설정
"""
 
import sys
import os
import xml.etree.ElementTree as ET
 
import requests
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KEYWORDS, REGIONS, ALWAYS_INCLUDE_ORGS, LH_SERVICE_KEY
from scrapers._common import is_deadline_in_range
 
ENDPOINT = "http://openapi.ebid.lh.or.kr/ebid.com.openapi.service.OpenBidInfoList.dev"
 
 
def _clean_key(key: str) -> str:
    import urllib.parse
    return urllib.parse.unquote(key)
 
 
def _matches_keyword(title: str) -> bool:
    return any(k in (title or "") for k in KEYWORDS)
 
 
def _matches_region(region_text: str, org_text: str = "") -> bool:
    if any(o in (org_text or "") for o in ALWAYS_INCLUDE_ORGS):
        return True
    if not region_text:
        return False
    return any(r in region_text for r in REGIONS)
 
 
def _xml_text(elem, *tag_candidates):
    """여러 후보 태그명 중 처음 발견되는 값을 반환 (LH 응답 필드명이 불확실해 후보를 여러 개 둠)"""
    for tag in tag_candidates:
        found = elem.find(tag)
        if found is not None and found.text:
            return found.text.strip()
    return ""
 
 
def fetch_lh_bids():
    """LH 입찰공고 중 통신 키워드 + 대상 지역에 해당하는 공고 리스트 반환"""
    if not LH_SERVICE_KEY:
        print("[LH] 서비스키(LH_SERVICE_KEY)가 설정되지 않아 건너뜁니다.")
        return []
 
    params = {
        "serviceKey": _clean_key(LH_SERVICE_KEY),
        "numOfRows": 500,
        "pageNo": 1,
    }
 
    try:
        resp = requests.get(ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"[LH] 요청 실패: {e}")
        try:
            print(f"[LH] 응답 내용(처음 300자): {resp.text[:300]}")
        except Exception:
            pass
        return []
 
    # 흔한 응답 구조: <response><body><items><item>...</item></items></body></response>
    items = root.findall(".//item")
    if not items:
        print(f"[LH] item 태그를 찾지 못함. 응답 최상위 태그: {root.tag}")
        return []
 
    results = []
    for item in items:
        title = _xml_text(item, "bidNm", "bidTitle", "cnsttNm")
        if not _matches_keyword(title):
            continue
        region_text = _xml_text(item, "rgnNm")
        if not _matches_region(region_text, "한국토지주택공사"):
            continue
        deadline = _xml_text(item, "bidClosDate", "bidClseDt")
        if not is_deadline_in_range(deadline):
            continue
 
        results.append({
            "source": "LH",
            "title": title,
            "org": "한국토지주택공사",
            "notice_no": _xml_text(item, "bidNo"),
            "region": region_text,
            "base_amount": _xml_text(item, "bssamt"),
            "notice_date": _xml_text(item, "ntceDate"),
            "deadline": deadline,
            "url": "https://ebid.lh.or.kr",
        })
 
    print(f"[LH] 총 {len(results)}건 수집")
    return results
 
 
if __name__ == "__main__":
    for b in fetch_lh_bids():
        print(b)
 
