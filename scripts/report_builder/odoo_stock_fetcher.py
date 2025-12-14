#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 재고 데이터 페처

Odoo에서 재고 이동(입고/출고) 데이터를 조회합니다.
"""

import xmlrpc.client
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class OdooStockFetcher:
    """Odoo 재고 데이터를 조회하는 클래스"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Args:
            url: Odoo 서버 URL
            db: 데이터베이스 이름
            username: 사용자 이메일
            password: API 키 또는 비밀번호
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        
        # SSL 컨텍스트
        self.ssl_context = ssl.create_default_context()
        
    def connect(self) -> bool:
        """Odoo에 연결합니다."""
        try:
            common_endpoint = f"{self.url}/xmlrpc/2/common"
            object_endpoint = f"{self.url}/xmlrpc/2/object"
            
            common = xmlrpc.client.ServerProxy(common_endpoint, context=self.ssl_context)
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                print("✗ Odoo 인증 실패")
                return False
            
            self.models = xmlrpc.client.ServerProxy(object_endpoint, context=self.ssl_context)
            print(f"✓ Odoo 연결 성공 (User ID: {self.uid})")
            return True
            
        except Exception as e:
            print(f"✗ Odoo 연결 오류: {e}")
            return False
    
    def _execute(self, model: str, method: str, *args, **kwargs):
        """Odoo API 호출을 실행합니다."""
        if not self.uid or not self.models:
            raise RuntimeError("먼저 connect()를 호출하세요.")
        
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def get_products(self, codes: List[str] = None, limit: int = None) -> List[dict]:
        """
        제품 목록을 조회합니다.
        
        Args:
            codes: 조회할 제품 코드 목록 (None이면 전체)
            limit: 최대 조회 개수
        
        Returns:
            제품 정보 목록
        """
        domain = []
        if codes:
            domain.append(['default_code', 'in', codes])
        
        kwargs = {
            'fields': ['id', 'name', 'default_code', 'uom_id', 'qty_available']
        }
        if limit:
            kwargs['limit'] = limit
        
        products = self._execute('product.product', 'search_read', domain, **kwargs)
        return products
    
    def get_stock_moves_by_date(self, date: str, product_codes: List[str] = None) -> Dict[str, dict]:
        """
        특정 날짜의 재고 이동을 조회합니다.
        
        Args:
            date: 조회 날짜 (YYYY-MM-DD 형식)
            product_codes: 조회할 제품 코드 목록 (None이면 전체)
        
        Returns:
            제품별 입고/출고 수량 딕셔너리
            {
                'PRODUCT-CODE': {
                    'incoming': 100.0,
                    'outgoing': 50.0,
                    'product_name': '제품명'
                }
            }
        """
        # 날짜 범위 설정
        date_start = f"{date} 00:00:00"
        date_end = f"{date} 23:59:59"
        
        # 기본 도메인
        base_domain = [
            ['state', '=', 'done'],  # 완료된 이동만
            ['date', '>=', date_start],
            ['date', '<=', date_end]
        ]
        
        # 제품 필터 추가
        if product_codes:
            # 먼저 제품 ID 조회
            products = self.get_products(codes=product_codes)
            product_ids = [p['id'] for p in products]
            if product_ids:
                base_domain.append(['product_id', 'in', product_ids])
        
        # 재고 이동 조회
        moves = self._execute(
            'stock.move', 'search_read',
            base_domain,
            fields=['product_id', 'product_uom_qty', 'location_id', 'location_dest_id']
        )
        
        # 결과 집계
        result = {}
        
        for move in moves:
            product_id = move['product_id'][0]
            product_name = move['product_id'][1]
            qty = move['product_uom_qty']
            
            # 위치 정보로 입고/출고 구분
            # 일반적으로: 외부 -> 내부 = 입고, 내부 -> 외부 = 출고
            location_id = move['location_id'][0]
            location_dest_id = move['location_dest_id'][0]
            
            if product_id not in result:
                result[product_id] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'incoming': 0.0,
                    'outgoing': 0.0
                }
            
            # 위치 유형에 따라 입고/출고 판단
            # (실제로는 location usage를 확인해야 함)
            # 임시로: location_id가 더 작으면 입고로 가정
            if location_dest_id > location_id:
                result[product_id]['incoming'] += qty
            else:
                result[product_id]['outgoing'] += qty
        
        return result
    
    def get_stock_moves_detailed(self, date: str) -> Tuple[List[dict], List[dict]]:
        """
        특정 날짜의 입고/출고를 상세하게 조회합니다.
        
        Args:
            date: 조회 날짜 (YYYY-MM-DD 형식)
        
        Returns:
            (입고 목록, 출고 목록) 튜플
        """
        date_start = f"{date} 00:00:00"
        date_end = f"{date} 23:59:59"
        
        # 입고 조회 (Suppliers/Vendors -> Stock)
        incoming_domain = [
            ['state', '=', 'done'],
            ['date', '>=', date_start],
            ['date', '<=', date_end],
            ['picking_type_id.code', '=', 'incoming']  # 입고 유형
        ]
        
        incoming_moves = self._execute(
            'stock.move', 'search_read',
            incoming_domain,
            fields=['product_id', 'product_uom_qty', 'product_uom', 'reference']
        )
        
        # 출고 조회 (Stock -> Customers)
        outgoing_domain = [
            ['state', '=', 'done'],
            ['date', '>=', date_start],
            ['date', '<=', date_end],
            ['picking_type_id.code', '=', 'outgoing']  # 출고 유형
        ]
        
        outgoing_moves = self._execute(
            'stock.move', 'search_read',
            outgoing_domain,
            fields=['product_id', 'product_uom_qty', 'product_uom', 'reference']
        )
        
        return incoming_moves, outgoing_moves
    
    def get_monthly_stock_summary(self, year: int, month: int) -> Dict[str, dict]:
        """
        월별 재고 누계를 조회합니다.
        
        Args:
            year: 연도
            month: 월
        
        Returns:
            제품별 월간 입고/출고 누계
        """
        # 월 시작/끝 날짜
        date_start = f"{year}-{month:02d}-01 00:00:00"
        
        # 다음 달 계산
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        date_end = f"{next_year}-{next_month:02d}-01 00:00:00"
        
        # 입고 조회
        incoming = self._execute(
            'stock.move', 'search_read',
            [
                ['state', '=', 'done'],
                ['date', '>=', date_start],
                ['date', '<', date_end],
                ['picking_type_id.code', '=', 'incoming']
            ],
            fields=['product_id', 'product_uom_qty']
        )
        
        # 출고 조회
        outgoing = self._execute(
            'stock.move', 'search_read',
            [
                ['state', '=', 'done'],
                ['date', '>=', date_start],
                ['date', '<', date_end],
                ['picking_type_id.code', '=', 'outgoing']
            ],
            fields=['product_id', 'product_uom_qty']
        )
        
        # 집계
        result = {}
        
        for move in incoming:
            pid = move['product_id'][0]
            pname = move['product_id'][1]
            if pid not in result:
                result[pid] = {'product_name': pname, 'incoming': 0.0, 'outgoing': 0.0}
            result[pid]['incoming'] += move['product_uom_qty']
        
        for move in outgoing:
            pid = move['product_id'][0]
            pname = move['product_id'][1]
            if pid not in result:
                result[pid] = {'product_name': pname, 'incoming': 0.0, 'outgoing': 0.0}
            result[pid]['outgoing'] += move['product_uom_qty']
        
        return result
    
    def get_current_stock(self, product_codes: List[str] = None) -> Dict[str, float]:
        """
        현재 재고 수량을 조회합니다.
        
        Args:
            product_codes: 조회할 제품 코드 목록
        
        Returns:
            제품 코드별 재고 수량
        """
        domain = []
        if product_codes:
            domain.append(['default_code', 'in', product_codes])
        
        products = self._execute(
            'product.product', 'search_read',
            domain,
            fields=['default_code', 'name', 'qty_available']
        )
        
        return {
            p['default_code']: {
                'name': p['name'],
                'qty': p['qty_available']
            }
            for p in products if p['default_code']
        }
    
    def get_stock_quants(self, location_id: int = None) -> List[dict]:
        """
        재고 현황(stock.quant)을 조회합니다.
        
        Args:
            location_id: 특정 위치의 재고만 조회
        
        Returns:
            재고 현황 목록
        """
        domain = [['quantity', '>', 0]]
        if location_id:
            domain.append(['location_id', '=', location_id])
        
        quants = self._execute(
            'stock.quant', 'search_read',
            domain,
            fields=['product_id', 'location_id', 'quantity', 'reserved_quantity']
        )
        
        return quants


def create_fetcher_from_config(config_path: str = None) -> OdooStockFetcher:
    """
    설정 파일에서 OdooStockFetcher를 생성합니다.
    
    기본 설정을 사용하거나 JSON 설정 파일을 지정할 수 있습니다.
    """
    # 기본 설정 (odoo_api_connect.py와 동일)
    default_config = {
        "url": "https://capa-ai.odoo.com",
        "db": "capa-ai",
        "username": "jae@capa.ai",
        "password": "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"
    }
    
    if config_path:
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = default_config
    
    return OdooStockFetcher(
        url=config['url'],
        db=config['db'],
        username=config['username'],
        password=config['password']
    )


def main():
    """테스트 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo 재고 데이터 조회')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='조회 날짜 (YYYY-MM-DD)')
    parser.add_argument('--products', action='store_true', help='제품 목록 조회')
    parser.add_argument('--moves', action='store_true', help='재고 이동 조회')
    parser.add_argument('--stock', action='store_true', help='현재 재고 조회')
    parser.add_argument('--limit', type=int, default=10, help='조회 개수 제한')
    
    args = parser.parse_args()
    
    # 연결
    fetcher = create_fetcher_from_config()
    if not fetcher.connect():
        return 1
    
    print()
    
    # 제품 조회
    if args.products:
        print("=" * 50)
        print("제품 목록")
        print("=" * 50)
        products = fetcher.get_products(limit=args.limit)
        for p in products:
            print(f"  [{p.get('default_code', 'N/A'):>12}] {p['name']}")
            print(f"      재고: {p.get('qty_available', 0):,.0f} {p.get('uom_id', ['', ''])[1]}")
        print()
    
    # 재고 이동 조회
    if args.moves:
        print("=" * 50)
        print(f"재고 이동 ({args.date})")
        print("=" * 50)
        incoming, outgoing = fetcher.get_stock_moves_detailed(args.date)
        
        print(f"\n입고: {len(incoming)}건")
        for m in incoming[:args.limit]:
            print(f"  - {m['product_id'][1]}: {m['product_uom_qty']:,.0f}")
        
        print(f"\n출고: {len(outgoing)}건")
        for m in outgoing[:args.limit]:
            print(f"  - {m['product_id'][1]}: {m['product_uom_qty']:,.0f}")
        print()
    
    # 현재 재고 조회
    if args.stock:
        print("=" * 50)
        print("현재 재고")
        print("=" * 50)
        stock = fetcher.get_current_stock()
        for code, info in list(stock.items())[:args.limit]:
            print(f"  [{code:>12}] {info['name']}: {info['qty']:,.0f}")
        print()
    
    # 기본 동작
    if not any([args.products, args.moves, args.stock]):
        print("사용 가능한 옵션:")
        print("  --products  제품 목록 조회")
        print("  --moves     재고 이동 조회")
        print("  --stock     현재 재고 조회")
        print("  --date      조회 날짜 지정")
    
    return 0


if __name__ == "__main__":
    exit(main())

