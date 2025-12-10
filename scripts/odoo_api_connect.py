#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Cloud API 접속 스크립트

Odoo 클라우드 서비스에 XML-RPC API로 접속합니다.
"""

import xmlrpc.client
import json
import ssl

# ============================================
# 설정 - 아래 값들을 수정하세요
# ============================================
ODOO_URL = "https://capa-ai.odoo.com"
ODOO_DB = "capa-ai"  # 데이터베이스 이름 (보통 서브도메인과 동일)
ODOO_USERNAME = "jae@capa.ai"  # 로그인 이메일
ODOO_PASSWORD = "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"  # API 키


def connect_to_odoo():
    """Odoo API에 연결하고 인증합니다."""
    
    # SSL 컨텍스트 설정 (클라우드 서비스용)
    context = ssl.create_default_context()
    
    # 공통 엔드포인트
    common_endpoint = f"{ODOO_URL}/xmlrpc/2/common"
    object_endpoint = f"{ODOO_URL}/xmlrpc/2/object"
    
    print("=" * 50)
    print("Odoo Cloud API 접속 테스트")
    print("=" * 50)
    print(f"URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Username: {ODOO_USERNAME}")
    print("=" * 50)
    
    try:
        # 1. 서버 버전 확인 (인증 불필요)
        print("\n1. 서버 버전 확인 중...")
        common = xmlrpc.client.ServerProxy(common_endpoint, context=context)
        version = common.version()
        print(f"   ✓ Odoo 버전: {version.get('server_version', 'Unknown')}")
        print(f"   ✓ 서버 시리즈: {version.get('server_serie', 'Unknown')}")
        
        # 2. 인증 (로그인)
        print("\n2. 인증 중...")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if uid:
            print(f"   ✓ 인증 성공! 사용자 ID: {uid}")
        else:
            print("   ✗ 인증 실패! 이메일과 비밀번호를 확인하세요.")
            return None, None
        
        # 3. 모델 접근 테스트
        print("\n3. 데이터 접근 테스트 중...")
        models = xmlrpc.client.ServerProxy(object_endpoint, context=context)
        
        # 사용자 정보 조회
        user_info = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'read',
            [[uid]],
            {'fields': ['name', 'login', 'company_id']}
        )
        
        if user_info:
            print(f"   ✓ 사용자 이름: {user_info[0].get('name')}")
            print(f"   ✓ 로그인: {user_info[0].get('login')}")
            company = user_info[0].get('company_id')
            if company:
                print(f"   ✓ 회사: {company[1]}")
        
        print("\n" + "=" * 50)
        print("API 접속 성공!")
        print("=" * 50)
        
        return uid, models
        
    except xmlrpc.client.Fault as e:
        print(f"\n✗ Odoo 오류: {e.faultString}")
        return None, None
    except Exception as e:
        print(f"\n✗ 연결 오류: {str(e)}")
        return None, None


def get_installed_modules(uid, models):
    """설치된 모듈 목록을 조회합니다."""
    if not uid or not models:
        print("먼저 connect_to_odoo()를 실행하세요.")
        return
    
    print("\n설치된 모듈 조회 중...")
    
    modules = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.module.module', 'search_read',
        [[['state', '=', 'installed']]],
        {'fields': ['name', 'shortdesc'], 'limit': 20}
    )
    
    print(f"\n설치된 모듈 (최대 20개):")
    for mod in modules:
        print(f"  - {mod['name']}: {mod['shortdesc']}")
    
    return modules


def get_products(uid, models, limit=10):
    """제품 목록을 조회합니다."""
    if not uid or not models:
        print("먼저 connect_to_odoo()를 실행하세요.")
        return
    
    print(f"\n제품 조회 중 (최대 {limit}개)...")
    
    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'search_read',
        [[]],
        {'fields': ['name', 'default_code', 'list_price', 'qty_available'], 'limit': limit}
    )
    
    print(f"\n제품 목록:")
    for prod in products:
        print(f"  - [{prod.get('default_code', 'N/A')}] {prod['name']}")
        print(f"    가격: {prod.get('list_price', 0):,.0f}원, 재고: {prod.get('qty_available', 0):,.0f}")
    
    return products


def get_partners(uid, models, limit=10):
    """파트너(고객/공급업체) 목록을 조회합니다."""
    if not uid or not models:
        print("먼저 connect_to_odoo()를 실행하세요.")
        return
    
    print(f"\n파트너 조회 중 (최대 {limit}개)...")
    
    partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_read',
        [[['is_company', '=', True]]],
        {'fields': ['name', 'email', 'phone', 'city'], 'limit': limit}
    )
    
    print(f"\n파트너 목록:")
    for partner in partners:
        print(f"  - {partner['name']}")
        if partner.get('email'):
            print(f"    이메일: {partner['email']}")
        if partner.get('city'):
            print(f"    도시: {partner['city']}")
    
    return partners


def create_product(uid, models, name, price, code=None):
    """새 제품을 생성합니다."""
    if not uid or not models:
        print("먼저 connect_to_odoo()를 실행하세요.")
        return
    
    print(f"\n제품 생성 중: {name}")
    
    product_data = {
        'name': name,
        'list_price': price,
        'type': 'product',
    }
    
    if code:
        product_data['default_code'] = code
    
    try:
        product_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'create',
            [product_data]
        )
        print(f"✓ 제품 생성 성공! ID: {product_id}")
        return product_id
    except Exception as e:
        print(f"✗ 제품 생성 실패: {e}")
        return None


# ============================================
# 메인 실행
# ============================================
if __name__ == "__main__":
    # 1. 연결 테스트
    uid, models = connect_to_odoo()
    
    if uid and models:
        # 2. 데이터 조회 예시
        print("\n" + "=" * 50)
        print("데이터 조회 테스트")
        print("=" * 50)
        
        # 설치된 모듈 조회
        # get_installed_modules(uid, models)
        
        # 제품 조회
        get_products(uid, models, limit=5)
        
        # 파트너 조회
        get_partners(uid, models, limit=5)
        
        # 제품 생성 예시 (주석 해제하여 사용)
        # create_product(uid, models, "테스트 제품", 10000, "TEST-001")

