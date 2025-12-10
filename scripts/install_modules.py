#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 모듈 설치 스크립트
"""

import xmlrpc.client
import ssl
import time

# 설정
ODOO_URL = "https://capa-ai.odoo.com"
ODOO_DB = "capa-ai"
ODOO_USERNAME = "jae@capa.ai"
ODOO_PASSWORD = "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"


def install_modules():
    """필요한 모듈 설치"""
    
    context = ssl.create_default_context()
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", context=context)
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", context=context)
    
    # 인증
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        print("인증 실패!")
        return
    
    print("=" * 50)
    print("Odoo 모듈 설치")
    print("=" * 50)
    
    # 설치할 모듈 목록
    modules_to_install = [
        'sale_management',  # Sale (판매)
        'purchase',         # Purchase (구매)
        'mrp',              # Manufacturing (MRP/제조)
        'stock',            # Inventory (재고)
        'account',          # Accounting (회계)
    ]
    
    for module_name in modules_to_install:
        print(f"\n모듈 '{module_name}' 확인 중...")
        
        try:
            # 모듈 검색
            module_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]]
            )
            
            if not module_ids:
                print(f"   ⚠ 모듈 '{module_name}'을 찾을 수 없습니다.")
                continue
            
            # 모듈 상태 확인
            module_info = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'read',
                [module_ids],
                {'fields': ['name', 'state', 'shortdesc']}
            )
            
            module = module_info[0]
            print(f"   모듈: {module['shortdesc']} ({module['name']})")
            print(f"   현재 상태: {module['state']}")
            
            if module['state'] == 'installed':
                print(f"   ✓ 이미 설치되어 있습니다.")
                continue
            
            # 모듈 설치
            print(f"   설치 시작...")
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [module_ids]
            )
            print(f"   ✓ 설치 완료!")
            
            # 잠시 대기 (설치 후 안정화)
            time.sleep(2)
            
        except Exception as e:
            print(f"   ✗ 오류: {e}")
    
    print("\n" + "=" * 50)
    print("모듈 설치 완료!")
    print("=" * 50)
    
    # 설치된 모듈 확인
    print("\n현재 설치된 주요 모듈:")
    for module_name in modules_to_install:
        try:
            module_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]]
            )
            if module_ids:
                module_info = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.module.module', 'read',
                    [module_ids],
                    {'fields': ['name', 'state', 'shortdesc']}
                )
                module = module_info[0]
                status = "✓" if module['state'] == 'installed' else "✗"
                print(f"   {status} {module['shortdesc']}: {module['state']}")
        except:
            pass


if __name__ == "__main__":
    install_modules()

