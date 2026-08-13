"""
한국토지주택공사(LH) 입찰공고 수집기
공공데이터포털의 "한국토지주택공사 입찰공고정보" OpenAPI 사용
 
사전 준비:
1) https://www.data.go.kr 에서 "한국토지주택공사 입찰공고정보" 검색 → 활용신청 (자동승인)
2) 발급받은 서비스키를 환경변수 LH_SERVICE_KEY 로 설정
 
주의: LH e-Bid OpenAPI도 필드명이 바뀔 수 있습니다. 응답이 비어있다면
      data.go.kr 문서의 "출력결과(Response Element)" 표에서 최신 필드명을 확인하세요.
"""
 
import sys
import os
 
import requests
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KEYWORDS, REGIONS, LH_SERVICE_KEY
 
ENDPOINT = "https://openapi.ebid.lh.or.kr/ebid.com.openapi.service.OpenBidInfoList.dev"
 
 
def _clean_key(key: str) -> str:
    import urllib.parse
    return urllib.parse.unquote(key)
 
 
def _matches_keyword(title: str) -> bool:
    return any(k in (title or "") for k in KEYWORDS)
 
 
def _matches_region(region_text: str) -> bool:
    if not region_text:
        return True
    return any(r in region_text for r in REGIONS)
 
 
def fetch_lh_bids():
    """LH 입찰공고 중 통신 키워드 + 대상 지역에 해당하는 공고 리스트 반환"""
    if not LH_SERVICE_KEY:
        print("[LH] 서비스키(LH_SERVICE_KEY)가 설정되지 않아 건너뜁니다.")
        return []
 
    params = {
        "serviceKey": _clean_key(LH_SERVICE_KEY),
        "numOfRows": 500,
        "pageNo": 1,
        "resultType": "json",
    }
 
    try:
        resp = requests.get(ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[LH] 요청 실패: {e}")
        try:
            print(f"[LH] 응답 내용(처음 300자): {resp.text[:300]}")
        except Exception:
            pass
        return []
 
    items = (
        data.get("response", {}).get("body", {}).get("items", [])
        if isinstance(data, dict)
        else []
    )
    if isinstance(items, dict):
        items = items.get("item", [])
 
    results = []
    for item in items:
        title = item.get("bidNm") or item.get("bidTitle") or item.get("cnsttNm", "")
        if not _matches_keyword(title):
            continue
        region_text = item.get("rgnNm", "")
        if not _matches_region(region_text):
            continue
 
        results.append({
            "source": "LH",
            "title": title,
            "org": "한국토지주택공사",
            "notice_no": item.get("bidNo", ""),
            "region": region_text,
            "base_amount": item.get("bssamt", ""),
            "notice_date": item.get("ntceDate", ""),
            "deadline": item.get("bidClosDate", ""),
            "url": item.get("url", "https://ebid.lh.or.kr"),
        })
 
    print(f"[LH] 총 {len(results)}건 수집")
    return results
 
 
if __name__ == "__main__":
    for b in fetch_lh_bids():
        print(b)
