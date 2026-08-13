"""
메인 실행 스크립트
- 나라장터 / LH / 국방전자조달(D2B) 수집기를 모두 돌려 결과를 합칩니다.
- 기존에 저장된 data/bids.json과 병합하여 중복(같은 출처+공고번호)은 최신 정보로 갱신하고,
  최근 30일이 지난 공고는 목록에서 정리합니다.
- 마지막으로 대시보드(docs/index.html)를 다시 생성합니다.
"""
 
import json
import os
from datetime import datetime, timedelta
 
from config import DATA_DIR, BIDS_JSON_PATH
from scrapers.g2b import fetch_g2b_bids
from scrapers.lh import fetch_lh_bids
from scrapers.d2b import fetch_d2b_bids
from scrapers.kwater import fetch_kwater_bids
from scrapers.kepco import fetch_kepco_bids
from generate_dashboard import generate_dashboard
 
 
def _load_existing():
    if not os.path.exists(BIDS_JSON_PATH):
        return []
    try:
        with open(BIDS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
 
 
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
 
    existing = _load_existing()
 
    merged = {}
    for bid in existing:
        merged[_dedupe_key(bid)] = bid
    for bid in new_bids:
        bid["collected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        merged[_dedupe_key(bid)] = bid
 
    # 30일 지난 공고는 정리 (수집일 기준, collected_at 없는 옛 데이터는 유지)
    cutoff = datetime.now() - timedelta(days=30)
    kept = []
    for bid in merged.values():
        collected_at = bid.get("collected_at")
        if collected_at:
            try:
                if datetime.strptime(collected_at, "%Y-%m-%d %H:%M") < cutoff:
                    continue
            except ValueError:
                pass
        kept.append(bid)
 
    kept.sort(key=lambda b: b.get("collected_at", ""), reverse=True)
 
    with open(BIDS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
 
    print(f"총 {len(kept)}건 저장 ({BIDS_JSON_PATH})")
 
    generate_dashboard(kept)
 
 
if __name__ == "__main__":
    main()
