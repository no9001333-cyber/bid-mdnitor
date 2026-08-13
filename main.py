"""
메인 실행 스크립트
- 나라장터 / LH / 국방전자조달(D2B) / 한국수자원공사 / 한국전력공사 / 한국철도공사
  수집기를 모두 돌려 결과를 합칩니다.
- 매번 "오늘 새로 수집한 결과"로 완전히 새로 저장합니다 (예전 데이터와 병합하지 않음).
  이렇게 해야 필터 기준(지역/기간 등)을 바꿨을 때 예전에 저장된, 지금 기준에는
  더 이상 맞지 않는 공고가 계속 남아있는 문제가 생기지 않습니다.
  (참고: 공고별 메모는 브라우저에 별도로 저장되므로 이 초기화와 무관하게 유지됩니다)
- 마지막으로 대시보드(docs/index.html)를 다시 생성합니다.
"""
 
import json
import os
from datetime import datetime
 
from config import DATA_DIR, BIDS_JSON_PATH
from scrapers.g2b import fetch_g2b_bids
from scrapers.lh import fetch_lh_bids
from scrapers.d2b import fetch_d2b_bids
from scrapers.kwater import fetch_kwater_bids
from scrapers.kepco import fetch_kepco_bids
from scrapers.korail import fetch_korail_bids
from generate_dashboard import generate_dashboard
 
 
def _dedupe_key(bid):
    return f"{bid.get('source')}::{bid.get('notice_no') or bid.get('title')}"
 
 
def main():
    os.makedirs(DATA_DIR, exist_ok=True)
 
    new_bids = []
    new_bids += fetch_g2b_bids()
    new_bids += fetch_lh_bids()
    new_bids += fetch_d2b_bids()
    new_bids += fetch_kwater_bids()
    new_bids += fetch_kepco_bids()
    new_bids += fetch_korail_bids()
 
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
 
    # 같은 공고가 중복 수집됐을 경우 정리 (같은 출처+공고번호는 마지막 것만 유지)
    deduped = {}
    for bid in new_bids:
        bid["collected_at"] = now_str
        deduped[_dedupe_key(bid)] = bid
 
    kept = list(deduped.values())
    kept.sort(key=lambda b: b.get("deadline", ""))
 
    with open(BIDS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
 
    print(f"총 {len(kept)}건 저장 ({BIDS_JSON_PATH})")
 
    generate_dashboard(kept)
 
 
if __name__ == "__main__":
    main()
