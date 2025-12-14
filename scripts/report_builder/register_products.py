#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo에 Excel 템플릿 제품 등록

매핑 파일의 제품을 Odoo에 등록합니다.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from odoo_stock_fetcher import create_fetcher_from_config


def register_products(mapping_path: str, limit: int = None, dry_run: bool = False):
    """
    매핑 파일의 제품을 Odoo에 등록합니다.
    
    Args:
        mapping_path: 매핑 JSON 파일 경로
        limit: 등록할 최대 제품 수 (None이면 전체)
        dry_run: True면 실제 등록하지 않고 미리보기만
    """
    # 매핑 파일 로드
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    products = mapping['products']
    if limit:
        products = products[:limit]
    
    print(f"등록할 제품: {len(products)}개")
    print()
    
    if dry_run:
        print("=== DRY RUN 모드 (실제 등록 안함) ===")
        for i, p in enumerate(products, 1):
            print(f"{i:3}. [{p['odoo_product_code']}] {p['excel_name']}")
        return
    
    # Odoo 연결
    fetcher = create_fetcher_from_config()
    if not fetcher.connect():
        print("Odoo 연결 실패")
        return
    
    # 기존 제품 코드 조회 (중복 방지)
    existing = fetcher._execute(
        'product.product', 'search_read',
        [],
        fields=['default_code']
    )
    existing_codes = {p['default_code'] for p in existing if p['default_code']}
    print(f"기존 등록된 제품: {len(existing_codes)}개")
    print()
    
    # 제품 등록
    created = 0
    skipped = 0
    errors = []
    
    for i, p in enumerate(products, 1):
        code = p['odoo_product_code']
        name = p['excel_name']
        
        # 중복 체크
        if code in existing_codes:
            print(f"  [{i:3}] 건너뜀 (이미 존재): {code}")
            skipped += 1
            continue
        
        try:
            # 제품 생성 (Odoo 19.0 호환)
            product_data = {
                'name': name,
                'default_code': code,
                'type': 'consu',  # Odoo 19.0용 (Goods)
                'is_storable': True,  # 재고 추적 활성화
            }
            
            product_id = fetcher._execute(
                'product.product', 'create',
                product_data
            )
            
            print(f"  [{i:3}] ✓ 생성됨: [{code}] {name} (ID: {product_id})")
            created += 1
            existing_codes.add(code)  # 중복 방지
            
        except Exception as e:
            print(f"  [{i:3}] ✗ 오류: [{code}] {name} - {e}")
            errors.append((code, name, str(e)))
    
    print()
    print("=" * 50)
    print(f"결과: 생성 {created}개, 건너뜀 {skipped}개, 오류 {len(errors)}개")
    print("=" * 50)
    
    if errors:
        print("\n오류 목록:")
        for code, name, err in errors:
            print(f"  - [{code}] {name}: {err}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo에 제품 등록')
    parser.add_argument('-m', '--mapping', default='mappings/product_mapping.json',
                        help='매핑 파일 경로')
    parser.add_argument('-l', '--limit', type=int, default=50,
                        help='등록할 최대 제품 수 (기본: 50)')
    parser.add_argument('--all', action='store_true',
                        help='모든 제품 등록 (676개)')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 등록하지 않고 미리보기만')
    
    args = parser.parse_args()
    
    # 경로 결정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    mapping_path = args.mapping
    if not Path(mapping_path).is_absolute():
        mapping_path = project_root / mapping_path
    
    limit = None if args.all else args.limit
    
    register_products(
        mapping_path=str(mapping_path),
        limit=limit,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()

