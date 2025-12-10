# 설치 가이드

## 중요 사항

이 모듈의 디렉토리 이름이 `Odoo_Setting`인 경우, Odoo에서 모듈 이름으로 인식되지 않을 수 있습니다. 
더 나은 이름으로 변경하는 것을 권장합니다:

```bash
# 모듈 이름 변경 (예: oil_refining_demo)
mv Odoo_Setting oil_refining_demo
```

또는 디렉토리 이름을 그대로 사용하려면, 스크립트에서 모듈 이름을 수정해야 합니다.

## 설치 단계

### 1. 모듈 복사
```bash
# Odoo addons 디렉토리에 복사
cp -r oil_refining_demo /path/to/odoo/addons/
```

### 2. Odoo 설정
`odoo.conf` 파일에 addons 경로가 포함되어 있는지 확인:
```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/custom/addons
```

### 3. 모듈 설치
1. Odoo에 로그인
2. Apps 메뉴로 이동
3. "Update Apps List" 클릭
4. "Oil Refining Company Demo Data" 검색
5. Install 클릭

### 4. 주문 데이터 생성
모듈 설치 후, 주문 데이터를 생성해야 합니다:

**Odoo 쉘 사용:**
```bash
odoo shell -d your_database_name
```

쉘에서:
```python
# 모듈 이름 확인 (디렉토리 이름 사용)
import os
module_name = os.path.basename(os.path.dirname(__file__))

# 또는 직접 모듈 이름 지정
module_name = 'oil_refining_demo'  # 또는 'Odoo_Setting'

# 주문 생성
from odoo import api
env = api.Environment(api.Environment.manage().registry.cursor(), 1, {})

# 모듈 이름을 동적으로 가져오기
import importlib
module = importlib.import_module(f'{module_name}.scripts.create_orders')
module.create_all_orders(env)
```

**또는 간단하게:**
```python
# 모듈 이름을 직접 지정
exec(f"""
from {module_name}.scripts.create_orders import create_all_orders
from odoo import api
env = api.Environment(api.Environment.manage().registry.cursor(), 1, {{}})
create_all_orders(env)
""")
```

### 5. 추가 데이터 생성 (선택)
더 많은 데모 데이터를 생성하려면:
```python
from {module_name}.scripts.generate_demo_data import generate_all_demo_data
generate_all_demo_data(env)
```

## 문제 해결

### 모듈을 찾을 수 없는 경우
- 디렉토리 이름과 모듈 이름이 일치하는지 확인
- `__manifest__.py` 파일이 올바른지 확인
- Odoo 서버를 재시작

### 스크립트 실행 오류
- 모듈 이름을 올바르게 지정했는지 확인
- 필요한 의존성 모듈이 설치되어 있는지 확인 (product, stock, mrp, sale, purchase 등)

### 데이터가 생성되지 않는 경우
- 개발자 모드가 활성화되어 있는지 확인
- 데이터베이스 백업 후 다시 시도
- Odoo 로그 확인

