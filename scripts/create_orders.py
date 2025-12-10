#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 주문 데이터 생성 스크립트

이 스크립트는 판매 주문과 구매 주문을 생성합니다.
XML 파일보다 더 유연하게 날짜와 참조를 처리할 수 있습니다.
"""

from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def create_sale_orders(env):
    """판매 주문 생성"""
    print("판매 주문 생성 중...")
    
    SaleOrder = env['sale.order']
    
    # 판매 주문 데이터
    sale_orders_data = [
        {
            'partner': 'partner_customer_gs_caltex',
            'date_offset': -5,
            'state': 'sale',
            'lines': [
                {'product': 'product_gasoline_premium', 'qty': 50000, 'price': 1850},
                {'product': 'product_diesel_premium', 'qty': 80000, 'price': 1650},
            ]
        },
        {
            'partner': 'partner_customer_sk_energy',
            'date_offset': -3,
            'state': 'sale',
            'lines': [
                {'product': 'product_diesel_regular', 'qty': 60000, 'price': 1550},
                {'product': 'product_gasoline_regular', 'qty': 40000, 'price': 1750},
            ]
        },
        {
            'partner': 'partner_customer_s_oil',
            'date_offset': -2,
            'state': 'sale',
            'lines': [
                {'product': 'product_heavy_oil_bunker_c', 'qty': 100000, 'price': 650},
            ]
        },
        {
            'partner': 'partner_customer_lotte_chemical',
            'date_offset': -4,
            'state': 'sale',
            'lines': [
                {'product': 'product_chemical_ethylene', 'qty': 20000, 'price': 1200},
                {'product': 'product_chemical_propylene', 'qty': 15000, 'price': 1100},
                {'product': 'product_naphtha_light', 'qty': 30000, 'price': 950},
            ]
        },
        {
            'partner': 'partner_customer_hanwha_chemical',
            'date_offset': -1,
            'state': 'sale',
            'lines': [
                {'product': 'product_naphtha_heavy', 'qty': 25000, 'price': 900},
                {'product': 'product_chemical_propylene', 'qty': 10000, 'price': 1100},
            ]
        },
        {
            'partner': 'partner_customer_construction_company_1',
            'date_offset': 0,
            'state': 'draft',
            'lines': [
                {'product': 'product_asphalt_paving', 'qty': 50000, 'price': 450},
            ]
        },
        {
            'partner': 'partner_customer_shipping_company_1',
            'date_offset': -6,
            'state': 'sale',
            'lines': [
                {'product': 'product_heavy_oil_bunker_c', 'qty': 150000, 'price': 650},
            ]
        },
        {
            'partner': 'partner_customer_hyundai_oilbank',
            'date_offset': -7,
            'state': 'sale',
            'lines': [
                {'product': 'product_lpg', 'qty': 30000, 'price': 1200},
            ]
        },
    ]
    
    for order_data in sale_orders_data:
        try:
            partner = env.ref(f'oil_refining_demo.{order_data["partner"]}')
            date_order = datetime.now() + timedelta(days=order_data['date_offset'])
            
            order_lines = []
            for line_data in order_data['lines']:
                product = env.ref(f'oil_refining_demo.{line_data["product"]}')
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': line_data['qty'],
                    'price_unit': line_data['price'],
                }))
            
            order = SaleOrder.create({
                'partner_id': partner.id,
                'date_order': date_order.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': order_lines,
            })
            
            if order_data['state'] == 'sale':
                order.action_confirm()
        except Exception as e:
            print(f"판매 주문 생성 오류: {e}")
    
    print("판매 주문 생성 완료!")


def create_purchase_orders(env):
    """구매 주문 생성"""
    print("구매 주문 생성 중...")
    
    PurchaseOrder = env['purchase.order']
    
    # 구매 주문 데이터
    purchase_orders_data = [
        {
            'partner': 'partner_supplier_saudi_aramco',
            'date_offset': -10,
            'state': 'purchase',
            'lines': [
                {'product': 'product_crude_oil_arabian_light', 'qty': 500000, 'price': 800},
                {'product': 'product_crude_oil_arabian_heavy', 'qty': 300000, 'price': 700},
            ]
        },
        {
            'partner': 'partner_supplier_adnoc',
            'date_offset': -8,
            'state': 'purchase',
            'lines': [
                {'product': 'product_crude_oil_dubai', 'qty': 400000, 'price': 770},
            ]
        },
        {
            'partner': 'partner_supplier_exxonmobil',
            'date_offset': -12,
            'state': 'purchase',
            'lines': [
                {'product': 'product_crude_oil_wti', 'qty': 200000, 'price': 830},
            ]
        },
        {
            'partner': 'partner_supplier_shell',
            'date_offset': -15,
            'state': 'purchase',
            'lines': [
                {'product': 'product_crude_oil_arabian_light', 'qty': 250000, 'price': 800},
                {'product': 'product_crude_oil_dubai', 'qty': 150000, 'price': 770},
            ]
        },
        {
            'partner': 'partner_supplier_chevron',
            'date_offset': -9,
            'state': 'purchase',
            'lines': [
                {'product': 'product_crude_oil_wti', 'qty': 180000, 'price': 830},
            ]
        },
        {
            'partner': 'partner_supplier_saudi_aramco',
            'date_offset': -5,
            'state': 'draft',
            'lines': [
                {'product': 'product_crude_oil_arabian_heavy', 'qty': 350000, 'price': 700},
            ]
        },
    ]
    
    for order_data in purchase_orders_data:
        try:
            partner = env.ref(f'oil_refining_demo.{order_data["partner"]}')
            date_order = datetime.now() + timedelta(days=order_data['date_offset'])
            
            order_lines = []
            for line_data in order_data['lines']:
                product = env.ref(f'oil_refining_demo.{line_data["product"]}')
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_qty': line_data['qty'],
                    'price_unit': line_data['price'],
                }))
            
            order = PurchaseOrder.create({
                'partner_id': partner.id,
                'date_order': date_order.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': order_lines,
            })
            
            if order_data['state'] == 'purchase':
                order.button_confirm()
        except Exception as e:
            print(f"구매 주문 생성 오류: {e}")
    
    print("구매 주문 생성 완료!")


def create_all_orders(env=None):
    """모든 주문 생성"""
    if env is None:
        from odoo import api
        env = api.Environment(api.Environment.manage().registry.cursor(), SUPERUSER_ID, {})
    
    print("=" * 50)
    print("주문 데이터 생성 시작")
    print("=" * 50)
    
    try:
        create_sale_orders(env)
        create_purchase_orders(env)
        
        print("=" * 50)
        print("주문 데이터 생성 완료!")
        print("=" * 50)
    except Exception as e:
        print(f"오류 발생: {e}")
        raise


if __name__ == '__main__':
    # Odoo 쉘에서 실행할 때
    create_all_orders()

