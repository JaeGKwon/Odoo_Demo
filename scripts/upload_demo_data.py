#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
유류 정제 화학 회사 데모 데이터 업로드 스크립트
"""

import xmlrpc.client
import ssl

# 설정
ODOO_URL = "https://capa-ai.odoo.com"
ODOO_DB = "capa-ai"
ODOO_USERNAME = "jae@capa.ai"
ODOO_PASSWORD = "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"


class OdooAPI:
    def __init__(self):
        self.context = ssl.create_default_context()
        self.common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", context=self.context)
        self.models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", context=self.context)
        self.uid = None
        self.category_ids = {}
        self.product_ids = {}
        self.partner_ids = {}
        self.location_ids = {}
        
    def authenticate(self):
        """인증"""
        self.uid = self.common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if self.uid:
            print(f"✓ 인증 성공 (UID: {self.uid})")
            return True
        print("✗ 인증 실패")
        return False
    
    def execute(self, model, method, *args, **kwargs):
        """Odoo API 실행"""
        return self.models.execute_kw(
            ODOO_DB, self.uid, ODOO_PASSWORD,
            model, method, *args, **kwargs
        )
    
    def create_record(self, model, vals):
        """레코드 생성"""
        try:
            record_id = self.execute(model, 'create', [vals])
            return record_id
        except Exception as e:
            print(f"   ✗ 생성 실패: {e}")
            return None
    
    def search(self, model, domain, limit=None):
        """레코드 검색"""
        if limit:
            return self.execute(model, 'search', [domain], {'limit': limit})
        return self.execute(model, 'search', [domain])


def create_product_categories(api):
    """제품 카테고리 생성"""
    print("\n" + "=" * 50)
    print("1. 제품 카테고리 생성")
    print("=" * 50)
    
    # 기본 카테고리 찾기
    all_category = api.search('product.category', [('name', '=', 'All')], limit=1)
    parent_id = all_category[0] if all_category else False
    
    categories = [
        {'name': '원유', 'code': 'crude_oil'},
        {'name': '휘발유', 'code': 'gasoline'},
        {'name': '경유', 'code': 'diesel'},
        {'name': '중유', 'code': 'heavy_oil'},
        {'name': 'LPG', 'code': 'lpg'},
        {'name': '나프타', 'code': 'naphtha'},
        {'name': '아스팔트', 'code': 'asphalt'},
        {'name': '윤활유', 'code': 'lubricants'},
        {'name': '화학 원료', 'code': 'chemicals'},
        {'name': '부산물', 'code': 'byproducts'},
    ]
    
    for cat in categories:
        cat_id = api.create_record('product.category', {
            'name': cat['name'],
            'parent_id': parent_id,
        })
        if cat_id:
            api.category_ids[cat['code']] = cat_id
            print(f"   ✓ {cat['name']} (ID: {cat_id})")
        else:
            print(f"   ✗ {cat['name']} 생성 실패")
    
    print(f"\n   총 {len(api.category_ids)}개 카테고리 생성 완료")


def create_products(api):
    """제품 생성"""
    print("\n" + "=" * 50)
    print("2. 제품 생성")
    print("=" * 50)
    
    # UOM 찾기
    litre_uom = api.search('uom.uom', [('name', 'ilike', 'Liter')], limit=1)
    kg_uom = api.search('uom.uom', [('name', 'ilike', 'kg')], limit=1)
    
    litre_id = litre_uom[0] if litre_uom else False
    kg_id = kg_uom[0] if kg_uom else False
    
    if not litre_id:
        # Units 사용
        unit_uom = api.search('uom.uom', [('name', '=', 'Units')], limit=1)
        litre_id = unit_uom[0] if unit_uom else 1
        kg_id = unit_uom[0] if unit_uom else 1
    
    products = [
        # 원유
        {'name': '아라비아 라이트 원유', 'code': 'CRUDE-ARAB-LIGHT', 'category': 'crude_oil', 
         'price': 850, 'cost': 800, 'uom': litre_id, 'sale': False, 'purchase': True,
         'description': 'API 33-34도, 황 함량 1.8%'},
        {'name': '아라비아 헤비 원유', 'code': 'CRUDE-ARAB-HEAVY', 'category': 'crude_oil',
         'price': 750, 'cost': 700, 'uom': litre_id, 'sale': False, 'purchase': True,
         'description': 'API 27-28도, 황 함량 2.8%'},
        {'name': '두바이 원유', 'code': 'CRUDE-DUBAI', 'category': 'crude_oil',
         'price': 820, 'cost': 770, 'uom': litre_id, 'sale': False, 'purchase': True,
         'description': 'API 31도, 황 함량 2.0%'},
        {'name': 'WTI 원유', 'code': 'CRUDE-WTI', 'category': 'crude_oil',
         'price': 880, 'cost': 830, 'uom': litre_id, 'sale': False, 'purchase': True,
         'description': 'API 39-40도, 황 함량 0.24%'},
        
        # 휘발유
        {'name': '프리미엄 휘발유', 'code': 'GAS-PREM', 'category': 'gasoline',
         'price': 1850, 'cost': 1650, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '옥탄가 95 이상, 고급 휘발유'},
        {'name': '일반 휘발유', 'code': 'GAS-REG', 'category': 'gasoline',
         'price': 1750, 'cost': 1550, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '옥탄가 91, 일반 휘발유'},
        
        # 경유
        {'name': '프리미엄 경유', 'code': 'DIESEL-PREM', 'category': 'diesel',
         'price': 1650, 'cost': 1450, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '저유황 경유, 황 함량 10ppm 이하'},
        {'name': '일반 경유', 'code': 'DIESEL-REG', 'category': 'diesel',
         'price': 1550, 'cost': 1350, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '일반 경유, 황 함량 50ppm 이하'},
        
        # 중유
        {'name': '벙커C 중유', 'code': 'HEAVY-BUNKER-C', 'category': 'heavy_oil',
         'price': 650, 'cost': 550, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '선박용 중유, 점도 380cSt'},
        {'name': '산업용 중유', 'code': 'HEAVY-INDUST', 'category': 'heavy_oil',
         'price': 700, 'cost': 600, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '보일러용 중유'},
        
        # LPG
        {'name': '액화석유가스 (LPG)', 'code': 'LPG', 'category': 'lpg',
         'price': 1200, 'cost': 1000, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '프로판/부탄 혼합 가스'},
        
        # 나프타
        {'name': '경질 나프타', 'code': 'NAPHTHA-LIGHT', 'category': 'naphtha',
         'price': 950, 'cost': 850, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '화학 원료용 경질 나프타'},
        {'name': '중질 나프타', 'code': 'NAPHTHA-HEAVY', 'category': 'naphtha',
         'price': 900, 'cost': 800, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '화학 원료용 중질 나프타'},
        
        # 아스팔트
        {'name': '포장용 아스팔트', 'code': 'ASPHALT-PAVING', 'category': 'asphalt',
         'price': 450, 'cost': 350, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '도로 포장용 아스팔트'},
        {'name': '방수용 아스팔트', 'code': 'ASPHALT-ROOF', 'category': 'asphalt',
         'price': 500, 'cost': 400, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '지붕 방수용 아스팔트'},
        
        # 윤활유
        {'name': '엔진오일 5W-30', 'code': 'LUBE-ENGINE', 'category': 'lubricants',
         'price': 8500, 'cost': 7500, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '자동차용 엔진오일 5W-30'},
        {'name': '산업용 윤활유', 'code': 'LUBE-INDUST', 'category': 'lubricants',
         'price': 6500, 'cost': 5500, 'uom': litre_id, 'sale': True, 'purchase': False,
         'description': '기계용 산업 윤활유'},
        
        # 화학 원료
        {'name': '에틸렌', 'code': 'CHEM-ETHYLENE', 'category': 'chemicals',
         'price': 1200, 'cost': 1000, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '화학 원료용 에틸렌'},
        {'name': '프로필렌', 'code': 'CHEM-PROPYLENE', 'category': 'chemicals',
         'price': 1100, 'cost': 950, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '화학 원료용 프로필렌'},
        
        # 부산물
        {'name': '황', 'code': 'BYPROD-SULFUR', 'category': 'byproducts',
         'price': 300, 'cost': 200, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '정제 과정에서 생산되는 황'},
        {'name': '석유코크스', 'code': 'BYPROD-COKE', 'category': 'byproducts',
         'price': 250, 'cost': 150, 'uom': kg_id, 'sale': True, 'purchase': False,
         'description': '정제 과정에서 생산되는 석유코크스'},
    ]
    
    for prod in products:
        categ_id = api.category_ids.get(prod['category'], False)
        
        prod_vals = {
            'name': prod['name'],
            'default_code': prod['code'],
            'categ_id': categ_id,
            'is_storable': True,  # Odoo 19에서는 is_storable 사용
            'list_price': prod['price'],
            'standard_price': prod['cost'],
            'sale_ok': prod['sale'],
            'purchase_ok': prod['purchase'],
            'description': prod.get('description', ''),
        }
        
        # Odoo 19에서는 uom_po_id가 없음
        if prod['uom']:
            prod_vals['uom_id'] = prod['uom']
        
        prod_id = api.create_record('product.product', prod_vals)
        if prod_id:
            api.product_ids[prod['code']] = prod_id
            print(f"   ✓ [{prod['code']}] {prod['name']} (ID: {prod_id})")
        else:
            print(f"   ✗ [{prod['code']}] {prod['name']} 생성 실패")
    
    print(f"\n   총 {len(api.product_ids)}개 제품 생성 완료")


def create_partners(api):
    """파트너 (공급업체/고객) 생성"""
    print("\n" + "=" * 50)
    print("3. 파트너 생성 (공급업체 & 고객)")
    print("=" * 50)
    
    # 공급업체
    suppliers = [
        {'name': '사우디 아람코', 'code': 'supplier_aramco', 'city': 'Dhahran',
         'country': 'SA', 'email': 'procurement@aramco.com', 'phone': '+966-13-874-0000',
         'comment': '세계 최대 원유 생산 회사'},
        {'name': '아부다비 국영석유공사 (ADNOC)', 'code': 'supplier_adnoc', 'city': 'Abu Dhabi',
         'country': 'AE', 'email': 'sales@adnoc.ae', 'phone': '+971-2-602-0000',
         'comment': '아랍에미리트 국영 석유 회사'},
        {'name': '엑슨모빌 코리아', 'code': 'supplier_exxon', 'city': '서울특별시',
         'country': 'KR', 'email': 'korea@exxonmobil.com', 'phone': '+82-2-3456-7890',
         'comment': '엑슨모빌 한국 지사'},
        {'name': '셸 코리아', 'code': 'supplier_shell', 'city': '서울특별시',
         'country': 'KR', 'email': 'korea@shell.com', 'phone': '+82-2-3456-7891',
         'comment': '셸 한국 지사'},
        {'name': '셰브론 코리아', 'code': 'supplier_chevron', 'city': '서울특별시',
         'country': 'KR', 'email': 'korea@chevron.com', 'phone': '+82-2-3456-7892',
         'comment': '셰브론 한국 지사'},
    ]
    
    # 고객
    customers = [
        {'name': 'GS칼텍스', 'code': 'customer_gscaltex', 'city': '서울특별시',
         'email': 'contact@gscaltex.com', 'phone': '+82-2-2005-2005',
         'comment': '주요 정유 회사'},
        {'name': 'SK에너지', 'code': 'customer_skenergy', 'city': '서울특별시',
         'email': 'contact@skenergy.com', 'phone': '+82-2-2121-5114',
         'comment': 'SK그룹 계열 정유 회사'},
        {'name': 'S-OIL', 'code': 'customer_soil', 'city': '서울특별시',
         'email': 'contact@soil.co.kr', 'phone': '+82-2-2005-2005',
         'comment': '정유 회사'},
        {'name': '현대오일뱅크', 'code': 'customer_hyundai', 'city': '서울특별시',
         'email': 'contact@oilbank.co.kr', 'phone': '+82-2-3464-5114',
         'comment': '현대그룹 계열 정유 회사'},
        {'name': '롯데케미칼', 'code': 'customer_lotte', 'city': '서울특별시',
         'email': 'contact@lottechem.com', 'phone': '+82-2-829-4000',
         'comment': '화학 원료 구매 고객'},
        {'name': '한화케미칼', 'code': 'customer_hanwha', 'city': '서울특별시',
         'email': 'contact@hanwha-chem.com', 'phone': '+82-2-729-2000',
         'comment': '화학 원료 구매 고객'},
        {'name': '금호석유화학', 'code': 'customer_kumho', 'city': '서울특별시',
         'email': 'contact@kumho-petrochem.com', 'phone': '+82-2-2000-4000',
         'comment': '석유화학 제품 구매'},
        {'name': '대한건설', 'code': 'customer_construction', 'city': '서울특별시',
         'email': 'purchase@daehan-const.com', 'phone': '+82-2-3456-7000',
         'comment': '아스팔트 구매 고객'},
        {'name': '한국해운', 'code': 'customer_shipping', 'city': '서울특별시',
         'email': 'fuel@korea-shipping.com', 'phone': '+82-2-3456-8000',
         'comment': '벙커C 중유 구매 고객'},
    ]
    
    # 국가 코드 찾기
    def get_country_id(code):
        country = api.search('res.country', [('code', '=', code)], limit=1)
        return country[0] if country else False
    
    print("\n   [공급업체]")
    for sup in suppliers:
        country_id = get_country_id(sup.get('country', 'KR'))
        partner_vals = {
            'name': sup['name'],
            'is_company': True,
            'city': sup.get('city', ''),
            'email': sup.get('email', ''),
            'phone': sup.get('phone', ''),
            'comment': sup.get('comment', ''),
        }
        if country_id:
            partner_vals['country_id'] = country_id
            
        partner_id = api.create_record('res.partner', partner_vals)
        if partner_id:
            api.partner_ids[sup['code']] = partner_id
            print(f"   ✓ {sup['name']} (ID: {partner_id})")
    
    print("\n   [고객]")
    for cust in customers:
        country_id = get_country_id('KR')
        partner_vals = {
            'name': cust['name'],
            'is_company': True,
            'city': cust.get('city', ''),
            'email': cust.get('email', ''),
            'phone': cust.get('phone', ''),
            'comment': cust.get('comment', ''),
        }
        if country_id:
            partner_vals['country_id'] = country_id
            
        partner_id = api.create_record('res.partner', partner_vals)
        if partner_id:
            api.partner_ids[cust['code']] = partner_id
            print(f"   ✓ {cust['name']} (ID: {partner_id})")
    
    print(f"\n   총 {len(api.partner_ids)}개 파트너 생성 완료")


def create_stock_locations(api):
    """창고 위치 생성"""
    print("\n" + "=" * 50)
    print("4. 창고 위치 생성")
    print("=" * 50)
    
    # 기본 위치 찾기
    stock_location = api.search('stock.location', [('usage', '=', 'internal')], limit=1)
    parent_id = stock_location[0] if stock_location else False
    
    locations = [
        {'name': '원유 탱크 1호', 'code': 'crude_tank_1'},
        {'name': '원유 탱크 2호', 'code': 'crude_tank_2'},
        {'name': '원유 탱크 3호', 'code': 'crude_tank_3'},
        {'name': '휘발유 탱크 1호', 'code': 'gasoline_tank_1'},
        {'name': '휘발유 탱크 2호', 'code': 'gasoline_tank_2'},
        {'name': '경유 탱크 1호', 'code': 'diesel_tank_1'},
        {'name': '경유 탱크 2호', 'code': 'diesel_tank_2'},
        {'name': '중유 탱크', 'code': 'heavy_oil_tank'},
        {'name': 'LPG 탱크', 'code': 'lpg_tank'},
        {'name': '나프타 탱크', 'code': 'naphtha_tank'},
        {'name': '아스팔트 저장소', 'code': 'asphalt_storage'},
        {'name': '윤활유 저장소', 'code': 'lubricant_storage'},
        {'name': '화학 원료 저장소', 'code': 'chemical_storage'},
        {'name': '부산물 저장소', 'code': 'byproduct_storage'},
    ]
    
    for loc in locations:
        loc_vals = {
            'name': loc['name'],
            'usage': 'internal',
            'location_id': parent_id,
        }
        
        loc_id = api.create_record('stock.location', loc_vals)
        if loc_id:
            api.location_ids[loc['code']] = loc_id
            print(f"   ✓ {loc['name']} (ID: {loc_id})")
    
    print(f"\n   총 {len(api.location_ids)}개 위치 생성 완료")


def create_boms(api):
    """BOM (정제 공정) 생성"""
    print("\n" + "=" * 50)
    print("5. BOM (정제 공정) 생성")
    print("=" * 50)
    
    # 제품 템플릿 ID 찾기
    def get_template_id(product_code):
        if product_code in api.product_ids:
            prod = api.execute('product.product', 'read', [[api.product_ids[product_code]]], {'fields': ['product_tmpl_id']})
            if prod:
                return prod[0]['product_tmpl_id'][0]
        return False
    
    boms = [
        # 휘발유 정제
        {'product': 'GAS-PREM', 'qty': 1000, 'code': 'BOM-GAS-PREM',
         'lines': [('CRUDE-ARAB-LIGHT', 1200), ('NAPHTHA-LIGHT', 200)]},
        {'product': 'GAS-REG', 'qty': 1000, 'code': 'BOM-GAS-REG',
         'lines': [('CRUDE-DUBAI', 1150), ('NAPHTHA-LIGHT', 150)]},
        
        # 경유 정제
        {'product': 'DIESEL-PREM', 'qty': 1000, 'code': 'BOM-DIESEL-PREM',
         'lines': [('CRUDE-WTI', 1100), ('NAPHTHA-HEAVY', 100)]},
        {'product': 'DIESEL-REG', 'qty': 1000, 'code': 'BOM-DIESEL-REG',
         'lines': [('CRUDE-ARAB-HEAVY', 1050), ('NAPHTHA-HEAVY', 80)]},
        
        # 중유 정제
        {'product': 'HEAVY-BUNKER-C', 'qty': 1000, 'code': 'BOM-HEAVY-BUNKER',
         'lines': [('CRUDE-ARAB-HEAVY', 950)]},
        {'product': 'HEAVY-INDUST', 'qty': 1000, 'code': 'BOM-HEAVY-INDUST',
         'lines': [('CRUDE-DUBAI', 980)]},
        
        # LPG 정제
        {'product': 'LPG', 'qty': 1000, 'code': 'BOM-LPG',
         'lines': [('CRUDE-ARAB-LIGHT', 800), ('NAPHTHA-LIGHT', 300)]},
        
        # 나프타 정제
        {'product': 'NAPHTHA-LIGHT', 'qty': 1000, 'code': 'BOM-NAPHTHA-LIGHT',
         'lines': [('CRUDE-ARAB-LIGHT', 900)]},
        {'product': 'NAPHTHA-HEAVY', 'qty': 1000, 'code': 'BOM-NAPHTHA-HEAVY',
         'lines': [('CRUDE-DUBAI', 920)]},
        
        # 윤활유 정제
        {'product': 'LUBE-ENGINE', 'qty': 1000, 'code': 'BOM-LUBE-ENGINE',
         'lines': [('CRUDE-WTI', 700), ('NAPHTHA-LIGHT', 150)]},
        
        # 화학 원료
        {'product': 'CHEM-ETHYLENE', 'qty': 1000, 'code': 'BOM-ETHYLENE',
         'lines': [('NAPHTHA-LIGHT', 1200)]},
        {'product': 'CHEM-PROPYLENE', 'qty': 1000, 'code': 'BOM-PROPYLENE',
         'lines': [('NAPHTHA-HEAVY', 1150)]},
    ]
    
    created = 0
    for bom in boms:
        template_id = get_template_id(bom['product'])
        if not template_id:
            print(f"   ✗ {bom['code']} - 제품 템플릿 없음")
            continue
        
        # BOM 라인 준비
        bom_lines = []
        for line_code, line_qty in bom['lines']:
            line_prod_id = api.product_ids.get(line_code)
            if line_prod_id:
                bom_lines.append((0, 0, {
                    'product_id': line_prod_id,
                    'product_qty': line_qty,
                }))
        
        if not bom_lines:
            print(f"   ✗ {bom['code']} - BOM 라인 없음")
            continue
        
        bom_vals = {
            'product_tmpl_id': template_id,
            'product_qty': bom['qty'],
            'code': bom['code'],
            'type': 'normal',
            'bom_line_ids': bom_lines,
        }
        
        bom_id = api.create_record('mrp.bom', bom_vals)
        if bom_id:
            created += 1
            print(f"   ✓ {bom['code']} (ID: {bom_id})")
    
    print(f"\n   총 {created}개 BOM 생성 완료")


def create_sample_orders(api):
    """샘플 주문 생성"""
    print("\n" + "=" * 50)
    print("6. 샘플 주문 생성")
    print("=" * 50)
    
    from datetime import datetime, timedelta
    
    # 구매 주문 (원유 구매)
    print("\n   [구매 주문]")
    purchase_orders = [
        {'supplier': 'supplier_aramco', 'lines': [('CRUDE-ARAB-LIGHT', 50000, 800), ('CRUDE-ARAB-HEAVY', 30000, 700)]},
        {'supplier': 'supplier_adnoc', 'lines': [('CRUDE-DUBAI', 40000, 770)]},
        {'supplier': 'supplier_exxon', 'lines': [('CRUDE-WTI', 20000, 830)]},
    ]
    
    for po in purchase_orders:
        partner_id = api.partner_ids.get(po['supplier'])
        if not partner_id:
            continue
        
        order_lines = []
        for prod_code, qty, price in po['lines']:
            prod_id = api.product_ids.get(prod_code)
            if prod_id:
                order_lines.append((0, 0, {
                    'product_id': prod_id,
                    'product_qty': qty,
                    'price_unit': price,
                    'name': prod_code,
                }))
        
        if order_lines:
            po_vals = {
                'partner_id': partner_id,
                'order_line': order_lines,
            }
            po_id = api.create_record('purchase.order', po_vals)
            if po_id:
                print(f"   ✓ PO (ID: {po_id}) - {po['supplier']}")
    
    # 판매 주문
    print("\n   [판매 주문]")
    sale_orders = [
        {'customer': 'customer_gscaltex', 'lines': [('GAS-PREM', 5000, 1850), ('DIESEL-PREM', 8000, 1650)]},
        {'customer': 'customer_skenergy', 'lines': [('GAS-REG', 4000, 1750), ('DIESEL-REG', 6000, 1550)]},
        {'customer': 'customer_shipping', 'lines': [('HEAVY-BUNKER-C', 15000, 650)]},
        {'customer': 'customer_lotte', 'lines': [('CHEM-ETHYLENE', 2000, 1200), ('NAPHTHA-LIGHT', 3000, 950)]},
    ]
    
    for so in sale_orders:
        partner_id = api.partner_ids.get(so['customer'])
        if not partner_id:
            continue
        
        order_lines = []
        for prod_code, qty, price in so['lines']:
            prod_id = api.product_ids.get(prod_code)
            if prod_id:
                order_lines.append((0, 0, {
                    'product_id': prod_id,
                    'product_uom_qty': qty,
                    'price_unit': price,
                }))
        
        if order_lines:
            so_vals = {
                'partner_id': partner_id,
                'order_line': order_lines,
            }
            so_id = api.create_record('sale.order', so_vals)
            if so_id:
                print(f"   ✓ SO (ID: {so_id}) - {so['customer']}")
    
    print("\n   주문 생성 완료")


def main():
    """메인 실행"""
    print("=" * 50)
    print("유류 정제 화학 회사 데모 데이터 업로드")
    print("=" * 50)
    
    api = OdooAPI()
    
    if not api.authenticate():
        return
    
    try:
        # 1. 제품 카테고리 생성
        create_product_categories(api)
        
        # 2. 제품 생성
        create_products(api)
        
        # 3. 파트너 생성
        create_partners(api)
        
        # 4. 창고 위치 생성
        create_stock_locations(api)
        
        # 5. BOM 생성
        create_boms(api)
        
        # 6. 샘플 주문 생성
        create_sample_orders(api)
        
        print("\n" + "=" * 50)
        print("🎉 데모 데이터 업로드 완료!")
        print("=" * 50)
        print(f"\n생성된 데이터:")
        print(f"  - 제품 카테고리: {len(api.category_ids)}개")
        print(f"  - 제품: {len(api.product_ids)}개")
        print(f"  - 파트너: {len(api.partner_ids)}개")
        print(f"  - 창고 위치: {len(api.location_ids)}개")
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        raise


if __name__ == "__main__":
    main()

