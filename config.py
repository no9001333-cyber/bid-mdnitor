"""
공통 설정 파일
- 검색 키워드 / 대상 지역 / API 키를 여기서 관리합니다.
- API 키는 절대 코드에 직접 적지 말고, 환경변수(GitHub Actions Secrets)로 주입합니다.
"""
 
import os
 
# ── 검색 키워드 (공고명에 아래 단어 중 하나라도 포함되면 "통신공사" 관련으로 판단) ──
KEYWORDS = ["통신", "정보통신", "네트워크", "광통신", "무선통신"]
 
# ── 대상 지역 (공고의 지역/참가가능지역 정보에 아래 단어가 포함되면 통과) ──
# "전국"으로 공고된 건은 지역 필터와 무관하게 항상 포함됩니다.
REGIONS = ["용인", "경기", "전국"]
 
# ── 발주기관에 아래 단어가 포함되면, 지역 정보와 무관하게 항상 포함 ──
# (한전/철도공단처럼 전국구 발주기관은 지역 필드가 비어있어도 실제로는 전국 대상인 경우가 많음)
# 주의: "조달청"은 넣지 않음 — 지방조달청이 대행하는 공고는 실제 사업장이 특정 지역에
# 한정된 경우가 대부분이라, 여기 넣으면 지역 필터가 사실상 무력화됨.
ALWAYS_INCLUDE_ORGS = [
    "한국전력공사", "한국철도공사", "국가철도공단",
]
 
# ── 투찰마감까지 남은 일수 범위 (이 범위 밖의 공고는 목록에서 제외) ──
# 너무 임박하면 준비할 시간이 없고, 너무 멀면 아직 실익이 없어서 기본값을 7~30일로 둠.
MIN_DAYS_UNTIL_DEADLINE = 7
MAX_DAYS_UNTIL_DEADLINE = 30
 
# ── data.go.kr(공공데이터포털)에서 발급받은 서비스키 ──
# 나라장터: "조달청_나라장터 입찰공고정보서비스" 활용신청 후 발급
# LH:      "한국토지주택공사 입찰공고정보" 활용신청 후 발급
# 군부대(D2B): "방위사업청_군수품조달정보 입찰공고" 활용신청 후 발급
#            (참고: 군 공사 입찰공고는 법령상 나라장터에도 동시 공고되므로,
#             G2B 수집만으로도 상당수 군 공사 건이 함께 잡힙니다.)
G2B_SERVICE_KEY = os.environ.get("G2B_SERVICE_KEY", "")
LH_SERVICE_KEY = os.environ.get("LH_SERVICE_KEY", "")
D2B_SERVICE_KEY = os.environ.get("D2B_SERVICE_KEY", "")
KWATER_SERVICE_KEY = os.environ.get("KWATER_SERVICE_KEY", "")
KEPCO_API_KEY = os.environ.get("KEPCO_API_KEY", "")
KORAIL_SERVICE_KEY = os.environ.get("KORAIL_SERVICE_KEY", "")
 
# ── 조회 기간 (기본: 최근 N일 이내 공고) ──
# 매일 자동 수집이지만, 혹시 놓친 공고가 없도록 넉넉하게 30일치를 매번 다시 확인합니다.
# (data/bids.json에 계속 누적되므로 30일보다 오래된 공고도 한 번 수집되면 계속 남아있습니다)
LOOKBACK_DAYS = 30
 
# ── 산출물 경로 ──
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BIDS_JSON_PATH = os.path.join(DATA_DIR, "bids.json")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
DASHBOARD_HTML_PATH = os.path.join(DOCS_DIR, "index.html")
 
