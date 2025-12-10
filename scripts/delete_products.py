#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 제품 데이터 삭제 스크립트
"""

import xmlrpc.client
import ssl

# 설정
ODOO_URL = "https://capa-ai.odoo.com"
ODOO_DB = "capa-ai"
ODOO_USERNAME = "jae@capa.ai"
ODOO_PASSWORD = "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"


def delete_all_products():
    """모든 제품 삭제"""
    
    context = ssl.create_default_context()
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", context=context)
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", context=context)
    
    # 인증
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        print("인증 실패!")
        return
    
    print("=" * 50)
    print("기존 제품 데이터 삭제")
    print("=" * 50)
    
    # 1. 모든 제품 조회
    print("\n1. 기존 제품 조회 중...")
    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'search_read',
        [[]],
        {'fields': ['id', 'name', 'default_code']}
    )
    
    print(f"   총 {len(products)}개 제품 발견")
    
    if not products:
        print("   삭제할 제품이 없습니다.")
        return
    
    # 제품 목록 출력
    print("\n   삭제될 제품 목록:")
    for prod in products:
        code = prod.get('default_code') or 'N/A'
        print(f"   - [{code}] {prod['name']} (ID: {prod['id']})")
    
    # 2. 제품 삭제
    print(f"\n2. {len(products)}개 제품 삭제 중...")
    
    product_ids = [p['id'] for p in products]
    
    try:
        # product.product 삭제
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'unlink',
            [product_ids]
        )
        print(f"   ✓ product.product {len(product_ids)}개 삭제 완료")
    except Exception as e:
        print(f"   ✗ 삭제 오류: {e}")
        
        # 개별 삭제 시도
        print("\n   개별 삭제 시도 중...")
        deleted = 0
        failed = 0
        for prod in products:
            try:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.product', 'unlink',
                    [[prod['id']]]
                )
                deleted += 1
                print(f"   ✓ 삭제: {prod['name']}")
            except Exception as e2:
                failed += 1
                print(f"   ✗ 실패: {prod['name']} - {e2}")
        
        print(f"\n   결과: 삭제 {deleted}개, 실패 {failed}개")
    
    # 3. product.template도 삭제 (필요시)
    print("\n3. 제품 템플릿 정리 중...")
    templates = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.template', 'search_read',
        [[]],
        {'fields': ['id', 'name']}
    )
    
    if templates:
        template_ids = [t['id'] for t in templates]
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.template', 'unlink',
                [template_ids]
            )
            print(f"   ✓ product.template {len(template_ids)}개 삭제 완료")
        except Exception as e:
            print(f"   ⚠ 템플릿 삭제 중 오류 (무시 가능): {e}")
    
    # 4. 확인
    print("\n4. 삭제 확인 중...")
    remaining = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'search_count',
        [[]]
    )
    print(f"   남은 제품 수: {remaining}")
    
    print("\n" + "=" * 50)
    print("삭제 완료!")
    print("=" * 50)


if __name__ == "__main__":
    delete_all_products()

