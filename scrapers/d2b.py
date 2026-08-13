"""
방위사업청 국방전자조달시스템(D2B) 입찰공고 수집기
공공데이터포털의 "방위사업청_군수품조달정보 입찰공고" OpenAPI (국내 경쟁입찰공고) 사용

사전 준비:
1) https://www.data.go.kr 에서 "방위사업청 군수품조달정보 입찰공고" 검색 → 활용신청
   (개발계정 트래픽이 1일 100건으로 적으니, 실제 운영 시 활용사례 등록으로 트래픽 증설 권장)
2) 발급받은 서비스키를 환경변수 D2B_SERVICE_KEY 로 설정

참고: 법령상 군 공사(시설) 입찰공고는 나라장터에도 동시 공고되므로,
      g2b.py 수집 결과에 이미 상당수 군부대 공사 건이 포함되어 있을 수 있습니다.
      이 모듈은 D2B에만 별도로 뜨는 건을 보완적으로 잡기 위한 용도입니다.
"""

import sys
import os

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KEYWORDS, REGIONS, D2B_SERVICE_KEY

ENDPOINT = "http://openapi.d2b.go.kr/openapi/service/BidPblancInfoService"
OPERATION = "getDmstcCmpetBidPblancList"  # 국내 경쟁입찰공고 목록


def _matches_keyword(title: str) -> bool:
    return any(k in (title or "") for k in KEYWORDS)


def _matches_region(region_text: str) -> bool:
    if not region_text:
        return True
    return any(r in region_text for r in REGIONS)


def fetch_d2b_bids():
    """국방전자조달 국내 경쟁입찰공고 중 통신 키워드 + 대상 지역에 해당하는 공고 리스트 반환"""
    if not D2B_SERVICE_KEY:
        print("[D2B] 서비스키(D2B_SERVICE_KEY)가 설정되지 않아 건너뜁니다.")
        return []

    url = f"{ENDPOINT}/{OPERATION}"
    params = {
        "serviceKey": D2B_SERVICE_KEY,
        "numOfRows": 500,
        "pageNo": 1,
        "type": "json",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[D2B] 요청 실패: {e}")
        return []

    body = data.get("response", {}).get("body", {}) if isinstance(data, dict) else {}
    items = body.get("items", [])
    if isinstance(items, dict):
        items = items.get("item", [])

    results = []
    for item in items:
        title = item.get("pblancNm") or item.get("bidNtceNm", "")
        if not _matches_keyword(title):
            continue
        region_text = item.get("dlvrPlaceNm", "") or item.get("rgnNm", "")
        if not _matches_region(region_text):
            continue

        results.append({
            "source": "국방전자조달(D2B)",
            "title": title,
            "org": item.get("dmndInsttNm", "") or item.get("ntceInsttNm", ""),
            "notice_no": item.get("pblancNo", ""),
            "region": region_text,
            "base_amount": item.get("presmptPrce", ""),
            "notice_date": item.get("pblancDt", ""),
            "deadline": item.get("bidClseDt", ""),
            "url": "https://www.d2b.go.kr",
        })

    print(f"[D2B] 총 {len(results)}건 수집")
    return results


if __name__ == "__main__":
    for b in fetch_d2b_bids():
        print(b)
