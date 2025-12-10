#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 유류 정제 회사 데모 데이터 생성 스크립트

이 스크립트는 Odoo에서 실행하여 추가 데모 데이터를 생성합니다.
더 많은 제조 주문, 재고 이동, 재고 수량 등을 생성합니다.
"""

from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta
import random


def generate_stock_quant(env):
    """재고 수량 생성"""
    print("재고 수량 생성 중...")
    
    # 원유 재고
    crude_oil_products = [
        'product_crude_oil_arabian_light',
        'product_crude_oil_arabian_heavy',
        'product_crude_oil_dubai',
        'product_crude_oil_wti',
    ]
    
    # 완제품 재고
    finished_products = [
        'product_gasoline_premium',
        'product_gasoline_regular',
        'product_diesel_premium',
        'product_diesel_regular',
        'product_heavy_oil_bunker_c',
        'product_heavy_oil_industrial',
        'product_lpg',
        'product_naphtha_light',
        'product_naphtha_heavy',
        'product_asphalt_paving',
        'product_asphalt_roofing',
        'product_lubricant_engine_oil',
        'product_lubricant_industrial',
        'product_chemical_ethylene',
        'product_chemical_propylene',
    ]
    
    # 부산물 재고
    byproducts = [
        'product_byproduct_sulfur',
        'product_byproduct_coke',
    ]
    
    StockQuant = env['stock.quant']
    StockLocation = env['stock.location']
    
    # 원유 탱크에 재고 생성
    for product_ref in crude_oil_products:
        try:
            product = env.ref(f'oil_refining_demo.{product_ref}')
            location = StockLocation.search([
                ('name', 'like', '원유 탱크')
            ], limit=1)
            
            if location:
                StockQuant.create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'quantity': random.randint(100000, 500000),
                })
        except Exception as e:
            print(f"재고 생성 오류 ({product_ref}): {e}")
    
    # 완제품 탱크에 재고 생성
    for product_ref in finished_products:
        try:
            product = env.ref(f'oil_refining_demo.{product_ref}')
            location = StockLocation.search([
                ('name', 'like', product.categ_id.name)
            ], limit=1)
            
            if not location:
                location = StockLocation.search([
                    ('usage', '=', 'internal')
                ], limit=1)
            
            if location:
                StockQuant.create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'quantity': random.randint(10000, 100000),
                })
        except Exception as e:
            print(f"재고 생성 오류 ({product_ref}): {e}")
    
    # 부산물 저장소에 재고 생성
    for product_ref in byproducts:
        try:
            product = env.ref(f'oil_refining_demo.{product_ref}')
            location = StockLocation.search([
                ('name', 'like', '부산물')
            ], limit=1)
            
            if location:
                StockQuant.create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'quantity': random.randint(5000, 50000),
                })
        except Exception as e:
            print(f"재고 생성 오류 ({product_ref}): {e}")
    
    print("재고 수량 생성 완료!")


def generate_manufacturing_orders(env):
    """제조 주문 생성"""
    print("제조 주문 생성 중...")
    
    MrpProduction = env['mrp.production']
    
    # 제조할 제품 목록
    products_to_manufacture = [
        ('product_gasoline_premium', 50000),
        ('product_gasoline_regular', 40000),
        ('product_diesel_premium', 60000),
        ('product_diesel_regular', 50000),
        ('product_heavy_oil_bunker_c', 80000),
        ('product_lpg', 30000),
        ('product_naphtha_light', 35000),
        ('product_naphtha_heavy', 30000),
    ]
    
    for product_ref, qty in products_to_manufacture:
        try:
            product = env.ref(f'oil_refining_demo.{product_ref}')
            bom = env['mrp.bom'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ], limit=1)
            
            if bom:
                # 과거 30일간의 제조 주문 생성
                for i in range(3):
                    date_planned_start = datetime.now() - timedelta(days=random.randint(1, 30))
                    
                    production = MrpProduction.create({
                        'product_id': product.id,
                        'product_qty': qty,
                        'product_uom_id': product.uom_id.id,
                        'bom_id': bom.id,
                        'date_planned_start': date_planned_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'origin': f'제조 주문 {product.name} - {date_planned_start.strftime("%Y-%m-%d")}',
                    })
                    
                    # 일부는 완료 상태로
                    if random.choice([True, False]):
                        production.action_confirm()
                        if random.choice([True, False]):
                            production.button_mark_done()
        except Exception as e:
            print(f"제조 주문 생성 오류 ({product_ref}): {e}")
    
    print("제조 주문 생성 완료!")


def generate_additional_sale_orders(env):
    """추가 판매 주문 생성"""
    print("추가 판매 주문 생성 중...")
    
    SaleOrder = env['sale.order']
    
    customers = [
        'partner_customer_gs_caltex',
        'partner_customer_sk_energy',
        'partner_customer_s_oil',
        'partner_customer_hyundai_oilbank',
        'partner_customer_lotte_chemical',
        'partner_customer_hanwha_chemical',
    ]
    
    products = [
        ('product_gasoline_premium', 1850),
        ('product_gasoline_regular', 1750),
        ('product_diesel_premium', 1650),
        ('product_diesel_regular', 1550),
        ('product_heavy_oil_bunker_c', 650),
        ('product_lpg', 1200),
        ('product_naphtha_light', 950),
        ('product_chemical_ethylene', 1200),
    ]
    
    for i in range(10):
        try:
            customer_ref = random.choice(customers)
            product_ref, price = random.choice(products)
            
            customer = env.ref(f'oil_refining_demo.{customer_ref}')
            product = env.ref(f'oil_refining_demo.{product_ref}')
            
            date_order = datetime.now() - timedelta(days=random.randint(1, 60))
            
            order = SaleOrder.create({
                'partner_id': customer.id,
                'date_order': date_order.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': random.randint(10000, 100000),
                    'price_unit': price,
                })],
            })
            
            # 일부는 확인/판매 상태로
            if random.choice([True, False]):
                order.action_confirm()
                if random.choice([True, False]):
                    order.action_done()
        except Exception as e:
            print(f"판매 주문 생성 오류: {e}")
    
    print("추가 판매 주문 생성 완료!")


def generate_additional_purchase_orders(env):
    """추가 구매 주문 생성"""
    print("추가 구매 주문 생성 중...")
    
    PurchaseOrder = env['purchase.order']
    
    suppliers = [
        'partner_supplier_saudi_aramco',
        'partner_supplier_adnoc',
        'partner_supplier_exxonmobil',
        'partner_supplier_shell',
        'partner_supplier_chevron',
    ]
    
    crude_oil_products = [
        ('product_crude_oil_arabian_light', 800),
        ('product_crude_oil_arabian_heavy', 700),
        ('product_crude_oil_dubai', 770),
        ('product_crude_oil_wti', 830),
    ]
    
    for i in range(8):
        try:
            supplier_ref = random.choice(suppliers)
            product_ref, price = random.choice(crude_oil_products)
            
            supplier = env.ref(f'oil_refining_demo.{supplier_ref}')
            product = env.ref(f'oil_refining_demo.{product_ref}')
            
            date_order = datetime.now() - timedelta(days=random.randint(1, 90))
            
            order = PurchaseOrder.create({
                'partner_id': supplier.id,
                'date_order': date_order.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_qty': random.randint(100000, 500000),
                    'price_unit': price,
                })],
            })
            
            # 일부는 확인/구매 상태로
            if random.choice([True, False]):
                order.button_confirm()
                if random.choice([True, False]):
                    order.button_done()
        except Exception as e:
            print(f"구매 주문 생성 오류: {e}")
    
    print("추가 구매 주문 생성 완료!")


def generate_all_demo_data(env=None):
    """모든 데모 데이터 생성"""
    if env is None:
        from odoo import api
        env = api.Environment(api.Environment.manage().registry.cursor(), SUPERUSER_ID, {})
    
    print("=" * 50)
    print("유류 정제 회사 데모 데이터 생성 시작")
    print("=" * 50)
    
    try:
        # 주문 데이터 생성 (create_orders.py에서 처리)
        from .create_orders import create_sale_orders, create_purchase_orders
        create_sale_orders(env)
        create_purchase_orders(env)
        
        generate_stock_quant(env)
        generate_manufacturing_orders(env)
        generate_additional_sale_orders(env)
        generate_additional_purchase_orders(env)
        
        print("=" * 50)
        print("데모 데이터 생성 완료!")
        print("=" * 50)
    except Exception as e:
        print(f"오류 발생: {e}")
        raise


if __name__ == '__main__':
    # Odoo 쉘에서 실행할 때
    generate_all_demo_data()

