#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
리포트 생성기

Odoo 재고 데이터를 조회하여 Excel 템플릿에 채우고 리포트를 생성합니다.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# 현재 디렉토리를 모듈 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from odoo_stock_fetcher import OdooStockFetcher, create_fetcher_from_config
from excel_filler import ExcelFiller


class ReportGenerator:
    """재고 리포트 생성기"""
    
    def __init__(self, 
                 mapping_path: str,
                 odoo_config: dict = None,
                 template_dir: str = None):
        """
        Args:
            mapping_path: 매핑 JSON 파일 경로
            odoo_config: Odoo 연결 설정 (None이면 기본값 사용)
            template_dir: 템플릿 디렉토리 경로
        """
        self.mapping_path = Path(mapping_path)
        self.template_dir = template_dir
        
        # Excel 채우기 엔진 초기화
        self.filler = ExcelFiller(
            mapping_path=str(self.mapping_path),
            template_dir=template_dir
        )
        
        # Odoo 연결 (지연 초기화)
        self.odoo_config = odoo_config or self._get_default_odoo_config()
        self.fetcher = None
        
    def _get_default_odoo_config(self) -> dict:
        """기본 Odoo 설정을 반환합니다."""
        return {
            "url": "https://capa-ai.odoo.com",
            "db": "capa-ai",
            "username": "jae@capa.ai",
            "password": "a190768e3e846f84cb2e2fd317a3c84f1606e6b7"
        }
    
    def connect_odoo(self) -> bool:
        """Odoo에 연결합니다."""
        if self.fetcher:
            return True
        
        self.fetcher = OdooStockFetcher(
            url=self.odoo_config['url'],
            db=self.odoo_config['db'],
            username=self.odoo_config['username'],
            password=self.odoo_config['password']
        )
        
        return self.fetcher.connect()
    
    def _map_odoo_to_excel(self, odoo_data: Dict[int, dict]) -> Dict[str, dict]:
        """
        Odoo 데이터를 Excel 매핑 형식으로 변환합니다.
        
        Args:
            odoo_data: Odoo에서 가져온 제품별 데이터
                {product_id: {'product_name': ..., 'incoming': ..., 'outgoing': ...}}
        
        Returns:
            Excel 매핑용 데이터
                {'제품코드': {'incoming': ..., 'outgoing': ..., 'unit': ...}}
        """
        result = {}
        
        for product_id, data in odoo_data.items():
            product_name = data.get('product_name', '')
            
            # Odoo 제품명에서 Excel 매핑 찾기
            mapping = self.filler.find_product(product_name)
            
            if mapping:
                excel_name = mapping.get('excel_name', product_name)
                result[excel_name] = {
                    'incoming': data.get('incoming', 0),
                    'outgoing': data.get('outgoing', 0),
                    'unit': 'L'  # 기본 단위
                }
        
        return result
    
    def generate_daily_report(self,
                               date: str = None,
                               person: str = None,
                               output_path: str = None) -> str:
        """
        일일 재고 리포트를 생성합니다.
        
        Args:
            date: 리포트 날짜 (YYYY-MM-DD), 기본: 오늘
            person: 담당자 이름
            output_path: 출력 파일 경로 (기본: output/재고현황_YYYY-MM-DD.xlsx)
        
        Returns:
            생성된 파일 경로
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if output_path is None:
            output_dir = self.mapping_path.parent.parent / 'output'
            output_path = str(output_dir / f"재고현황_{date}.xlsx")
        
        print("\n" + "=" * 60)
        print(f"재고 리포트 생성 - {date}")
        print("=" * 60)
        
        # 1. Odoo 연결
        print("\n[1/3] Odoo 연결 중...")
        if not self.connect_odoo():
            print("✗ Odoo 연결 실패")
            return None
        
        # 2. 재고 데이터 조회
        print(f"\n[2/3] 재고 데이터 조회 중 ({date})...")
        
        try:
            # 당일 입고/출고 조회
            stock_data = self.fetcher.get_stock_moves_by_date(date)
            print(f"  - 조회된 제품: {len(stock_data)}개")
            
            # Odoo 데이터를 Excel 형식으로 변환
            excel_data = self._map_odoo_to_excel(stock_data)
            print(f"  - 매핑된 제품: {len(excel_data)}개")
            
        except Exception as e:
            print(f"  ⚠ 데이터 조회 오류: {e}")
            print("  → 빈 리포트로 생성합니다.")
            excel_data = {}
        
        # 3. 리포트 생성
        print(f"\n[3/3] 리포트 생성 중...")
        
        result = self.filler.create_report(
            output_path=output_path,
            date=date,
            person=person,
            stock_data=excel_data
        )
        
        print("\n" + "=" * 60)
        print("✓ 리포트 생성 완료!")
        print(f"  파일: {result}")
        print("=" * 60)
        
        return result
    
    def generate_from_json(self, 
                           json_data: dict,
                           date: str = None,
                           person: str = None,
                           output_path: str = None) -> str:
        """
        JSON 데이터로 리포트를 생성합니다 (Odoo 연결 없이).
        
        Args:
            json_data: 재고 데이터 딕셔너리
                {
                    '제품코드': {'incoming': 100, 'outgoing': 50, 'unit': 'L'},
                    ...
                }
            date: 리포트 날짜
            person: 담당자
            output_path: 출력 경로
        
        Returns:
            생성된 파일 경로
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if output_path is None:
            output_dir = self.mapping_path.parent.parent / 'output'
            output_path = str(output_dir / f"재고현황_{date}.xlsx")
        
        print("\n" + "=" * 60)
        print(f"재고 리포트 생성 (JSON 데이터) - {date}")
        print("=" * 60)
        
        result = self.filler.create_report(
            output_path=output_path,
            date=date,
            person=person,
            stock_data=json_data
        )
        
        print("\n" + "=" * 60)
        print("✓ 리포트 생성 완료!")
        print(f"  파일: {result}")
        print("=" * 60)
        
        return result


def main():
    """메인 CLI 진입점"""
    parser = argparse.ArgumentParser(
        description='Odoo 재고 데이터로 Excel 리포트 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 오늘 날짜로 리포트 생성
  python report_generator.py

  # 특정 날짜로 리포트 생성
  python report_generator.py --date 2025-12-08

  # 담당자 지정
  python report_generator.py --date 2025-12-08 --person "배종건"

  # JSON 파일에서 데이터 읽어서 생성
  python report_generator.py --json data.json

  # 출력 경로 지정
  python report_generator.py -o output/my_report.xlsx
        """
    )
    
    parser.add_argument('-d', '--date', 
                        default=datetime.now().strftime('%Y-%m-%d'),
                        help='리포트 날짜 (YYYY-MM-DD), 기본: 오늘')
    
    parser.add_argument('-p', '--person',
                        default='담당자',
                        help='담당자 이름')
    
    parser.add_argument('-o', '--output',
                        help='출력 파일 경로')
    
    parser.add_argument('-m', '--mapping',
                        default='mappings/product_mapping.json',
                        help='매핑 파일 경로')
    
    parser.add_argument('--json',
                        help='JSON 데이터 파일 (Odoo 대신 사용)')
    
    parser.add_argument('--no-odoo', action='store_true',
                        help='Odoo 연결 없이 빈 템플릿 생성')
    
    parser.add_argument('--template-dir',
                        help='템플릿 파일 디렉토리')
    
    args = parser.parse_args()
    
    # 프로젝트 루트 디렉토리 결정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # 매핑 파일 경로 결정
    mapping_path = args.mapping
    if not Path(mapping_path).is_absolute():
        mapping_path = project_root / mapping_path
    
    try:
        generator = ReportGenerator(
            mapping_path=str(mapping_path),
            template_dir=args.template_dir or str(project_root)
        )
        
        if args.json:
            # JSON 파일에서 데이터 로드
            with open(args.json, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            generator.generate_from_json(
                json_data=json_data,
                date=args.date,
                person=args.person,
                output_path=args.output
            )
        elif args.no_odoo:
            # 빈 템플릿 생성
            generator.generate_from_json(
                json_data={},
                date=args.date,
                person=args.person,
                output_path=args.output
            )
        else:
            # Odoo에서 데이터 조회하여 생성
            generator.generate_daily_report(
                date=args.date,
                person=args.person,
                output_path=args.output
            )
        
        return 0
        
    except FileNotFoundError as e:
        print(f"✗ 파일을 찾을 수 없습니다: {e}")
        return 1
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

