# Odoo 유류 정제 화학 회사 데모 데이터

이 모듈은 유류(기름) 제품을 정제하는 화학 회사를 위한 포괄적인 Odoo 데모 데이터를 제공합니다.

## 개요

한국정유화학주식회사라는 가상의 유류 정제 회사를 위한 완전한 데모 시나리오를 제공합니다. 이 데모는 실제 정유 회사의 운영을 시뮬레이션하기 위해 설계되었습니다.

## 포함된 데이터

### 1. 회사 정보
- 회사명: 한국정유화학주식회사
- 위치: 울산광역시
- 산업: 유류 정제 및 화학 제품 생산

### 2. 제품 카테고리
- 원유 (Crude Oil)
- 휘발유 (Gasoline)
- 경유 (Diesel)
- 중유 (Heavy Oil)
- LPG (액화석유가스)
- 나프타 (Naphtha)
- 아스팔트 (Asphalt)
- 윤활유 (Lubricants)
- 화학 원료 (Chemical Feedstocks)
- 부산물 (Byproducts)

### 3. 제품 (총 20개 이상)

#### 원유 제품
- 아라비아 라이트 원유 (API 33-34도)
- 아라비아 헤비 원유 (API 27-28도)
- 두바이 원유 (API 31도)
- WTI 원유 (API 39-40도)

#### 정제 제품
- 프리미엄 휘발유 (옥탄가 95 이상)
- 일반 휘발유 (옥탄가 91)
- 프리미엄 경유 (저유황, 10ppm 이하)
- 일반 경유 (50ppm 이하)
- 벙커C 중유 (선박용)
- 산업용 중유
- 액화석유가스 (LPG)
- 경질/중질 나프타
- 포장용/방수용 아스팔트
- 엔진오일/산업용 윤활유
- 에틸렌/프로필렌 (화학 원료)
- 황/석유코크스 (부산물)

### 4. 파트너

#### 공급업체 (5개)
- 사우디 아람코
- 아부다비 국영석유공사 (ADNOC)
- 엑슨모빌 코리아
- 셸 코리아
- 셰브론 코리아

#### 고객 (10개)
- GS칼텍스
- SK에너지
- S-OIL
- 현대오일뱅크
- 롯데케미칼
- 한화케미칼
- 금호석유화학
- 대한건설
- 한국해운
- 기타 고객사

### 5. BOM (Bill of Materials)
각 정제 제품에 대한 BOM이 포함되어 있습니다:
- 휘발유 정제 BOM (원유 + 나프타)
- 경유 정제 BOM
- 중유 정제 BOM
- LPG 정제 BOM
- 나프타 정제 BOM
- 아스팔트 정제 BOM
- 윤활유 정제 BOM
- 화학 원료 정제 BOM
- 부산물 생산 BOM

### 6. 창고 및 위치
- 원료 창고
- 완제품 창고
- 부산물 창고
- 원유 탱크 (3개)
- 휘발유 탱크 (2개)
- 경유 탱크 (2개)
- 중유 탱크
- LPG 탱크
- 나프타 탱크
- 아스팔트 저장소
- 윤활유 저장소
- 화학 원료 저장소
- 부산물 저장소

### 7. 주문 데이터
- 판매 주문 (8개 이상)
- 구매 주문 (6개 이상)
- 제조 주문 (라우팅 포함)

### 8. 직원 및 부서
- 생산부
- 영업부
- 구매부
- 품질관리부
- 설비관리부

## 설치 방법

### 1. 모듈 설치
```bash
# Odoo 서버에 모듈 복사
cp -r Odoo_Setting /path/to/odoo/addons/

# 또는 Odoo 설정에서 addons_path에 이 디렉토리 추가
```

### 2. Odoo에서 모듈 설치
1. Odoo에 로그인
2. Apps 메뉴로 이동
3. "Oil Refining Company Demo Data" 검색
4. Install 클릭

### 3. 주문 데이터 생성 (필수)
판매 주문과 구매 주문은 Python 스크립트로 생성해야 합니다:

**방법 1: Odoo 쉘에서 실행**
```bash
# Odoo 쉘 실행
odoo shell -d your_database_name

# 쉘에서 실행
from oil_refining_demo.scripts.create_orders import create_all_orders
from odoo import api
env = api.Environment(api.Environment.manage().registry.cursor(), 1, {})
create_all_orders(env)
```

**방법 2: Odoo UI에서 (개발자 모드)**
1. 개발자 모드 활성화
2. Settings > Technical > Python Code
3. 다음 코드 실행:
```python
from oil_refining_demo.scripts.create_orders import create_all_orders
create_all_orders(env)
```

### 4. 추가 데이터 생성 (선택사항)
더 많은 데모 데이터(재고, 추가 주문 등)를 생성하려면:

```python
# Odoo 쉘에서 실행
from oil_refining_demo.scripts.generate_demo_data import generate_all_demo_data
from odoo import api
env = api.Environment(api.Environment.manage().registry.cursor(), 1, {})
generate_all_demo_data(env)
```

이 스크립트는 다음을 생성합니다:
- 재고 수량 (각 제품별)
- 추가 제조 주문
- 추가 판매/구매 주문

## 데이터 구조

```
Odoo_Setting/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   ├── company_data.xml          # 회사 정보
│   ├── product_categories.xml    # 제품 카테고리
│   ├── products.xml              # 제품 데이터
│   ├── partners.xml              # 공급업체 및 고객
│   ├── warehouses.xml            # 창고 및 위치
│   ├── boms.xml                  # BOM (정제 공정)
│   ├── manufacturing_orders.xml  # 제조 주문 라우팅
│   ├── sale_orders.xml           # 판매 주문
│   ├── purchase_orders.xml       # 구매 주문
│   └── employees.xml              # 직원 및 부서
└── scripts/
    └── generate_demo_data.py     # 추가 데이터 생성 스크립트
```

## 사용 시나리오

### 시나리오 1: 원유 구매 및 정제
1. 사우디 아람코로부터 원유 구매 주문 생성
2. 원유 입고 처리
3. 휘발유 제조 주문 생성 (BOM 사용)
4. 정제 공정 완료
5. 완제품 창고로 이동

### 시나리오 2: 고객 주문 처리
1. GS칼텍스로부터 휘발유 판매 주문 수신
2. 재고 확인
3. 판매 주문 확인
4. 납품 처리
5. 송장 발행

### 시나리오 3: 정제 공정 관리
1. 제조 주문 생성
2. 원료 소비 확인
3. 정제 공정 진행
4. 품질 검사
5. 완제품 생산 완료

## 주요 기능

- **완전한 제품 라인**: 원유부터 완제품까지 전체 제품 라인
- **현실적인 BOM**: 실제 정제 공정을 반영한 BOM 구조
- **다양한 파트너**: 국내외 주요 정유 회사 및 화학 회사
- **창고 관리**: 탱크 및 저장소를 포함한 상세한 창고 구조
- **주문 데이터**: 판매, 구매, 제조 주문 샘플 데이터

## 커스터마이징

데이터를 수정하려면 각 XML 파일을 편집하세요:
- 제품 추가/수정: `data/products.xml`
- 파트너 추가/수정: `data/partners.xml`
- BOM 수정: `data/boms.xml`
- 주문 데이터 수정: `data/sale_orders.xml`, `data/purchase_orders.xml`

## 주의사항

- 이 모듈은 데모 목적으로만 사용됩니다
- 실제 운영 환경에서 사용하기 전에 모든 데이터를 검토하세요
- 가격 및 수량은 예시이며, 실제 시장 가격과 다를 수 있습니다
- `noupdate="1"` 속성으로 인해 모듈 업데이트 시 데이터가 덮어쓰이지 않습니다

## 라이선스

이 모듈은 데모 목적으로 자유롭게 사용할 수 있습니다.

## 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

## 버전

- Version: 1.0
- Odoo 호환 버전: 14.0 이상

