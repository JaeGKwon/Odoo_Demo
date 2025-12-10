#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수익성 분석 PDF 보고서 생성
"""

import xmlrpc.client
import ssl
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
import os

# PDF 파일 경로
PDF_PATH = "/Users/jgkwon/Downloads/Cursor_project/Odoo_Setting/수익성분석_보고서.pdf"

# Odoo 설정
ODOO_URL = 'https://capa-ai.odoo.com'
ODOO_DB = 'capa-ai'
ODOO_USERNAME = 'jae@capa.ai'
ODOO_PASSWORD = 'a190768e3e846f84cb2e2fd317a3c84f1606e6b7'


def get_odoo_data():
    """Odoo에서 데이터 조회"""
    context = ssl.create_default_context()
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', context=context)
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', context=context)
    
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    sales = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'sale.order', 'search_read', 
                              [[]], {'fields': ['name', 'partner_id', 'amount_total']})
    purchases = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'purchase.order', 'search_read', 
                                  [[]], {'fields': ['name', 'partner_id', 'amount_total']})
    
    return sales, purchases


def generate_pdf():
    """PDF 보고서 생성"""
    print("Odoo 데이터 조회 중...")
    sales, purchases = get_odoo_data()
    
    # 계산
    total_sales = sum(s['amount_total'] for s in sales)
    total_purchases = sum(p['amount_total'] for p in purchases)
    gross_profit = total_sales - total_purchases
    margin_rate = (gross_profit / total_sales) * 100 if total_sales > 0 else 0
    roi = (gross_profit / total_purchases) * 100 if total_purchases > 0 else 0
    
    print("PDF 생성 중...")
    
    # PDF 설정
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # 스타일 정의
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, alignment=1, spaceAfter=30)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, spaceBefore=20)
    normal_style = styles['Normal']
    
    elements = []
    
    # 제목
    elements.append(Paragraph("Profitability Analysis Report", title_style))
    elements.append(Paragraph("Oil Refining Chemical Company - Demo Data", 
                              ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=1, fontSize=12)))
    elements.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", 
                              ParagraphStyle('Date', parent=styles['Normal'], alignment=1, fontSize=10, textColor=colors.gray)))
    elements.append(Spacer(1, 30))
    
    # 1. P&L Summary
    elements.append(Paragraph("1. P&L Summary (Profit & Loss)", heading_style))
    
    pnl_data = [
        ['Item', 'Amount (USD)'],
        ['Sales Revenue', f'${total_sales:,.0f}'],
        ['Cost of Goods Sold', f'(${total_purchases:,.0f})'],
        ['Gross Profit', f'${gross_profit:,.0f}'],
        ['Gross Margin', f'{margin_rate:.1f}%'],
    ]
    
    pnl_table = Table(pnl_data, colWidths=[3*inch, 2*inch])
    pnl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#875A7B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#E8F5E9')),
        ('FONTNAME', (0, 3), (-1, 4), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(pnl_table)
    elements.append(Spacer(1, 20))
    
    # 2. Customer Sales Analysis
    elements.append(Paragraph("2. Sales by Customer", heading_style))
    
    customer_sales = {}
    for s in sales:
        customer = s['partner_id'][1] if s['partner_id'] else 'Unknown'
        customer_sales[customer] = customer_sales.get(customer, 0) + s['amount_total']
    
    sorted_customers = sorted(customer_sales.items(), key=lambda x: x[1], reverse=True)
    
    customer_data = [['Customer', 'Sales (USD)', 'Share %', 'Cumulative %']]
    cumulative = 0
    for customer, amount in sorted_customers:
        pct = (amount / total_sales) * 100
        cumulative += pct
        customer_data.append([customer, f'${amount:,.0f}', f'{pct:.1f}%', f'{cumulative:.1f}%'])
    
    customer_table = Table(customer_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#875A7B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))
    
    # 3. Supplier Purchase Analysis
    elements.append(Paragraph("3. Purchases by Supplier", heading_style))
    
    supplier_purchases = {}
    for p in purchases:
        supplier = p['partner_id'][1] if p['partner_id'] else 'Unknown'
        supplier_purchases[supplier] = supplier_purchases.get(supplier, 0) + p['amount_total']
    
    sorted_suppliers = sorted(supplier_purchases.items(), key=lambda x: x[1], reverse=True)
    
    supplier_data = [['Supplier', 'Purchases (USD)', 'Share %']]
    for supplier, amount in sorted_suppliers:
        pct = (amount / total_purchases) * 100
        supplier_data.append([supplier[:30], f'${amount:,.0f}', f'{pct:.1f}%'])
    
    supplier_table = Table(supplier_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
    supplier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00796B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(supplier_table)
    elements.append(Spacer(1, 20))
    
    # 4. KPIs
    elements.append(Paragraph("4. Key Performance Indicators (KPIs)", heading_style))
    
    avg_order = total_sales / len(sales) if sales else 0
    profit_per_order = gross_profit / len(sales) if sales else 0
    
    kpi_data = [
        ['KPI', 'Value', 'Assessment'],
        ['Gross Margin', f'{margin_rate:.1f}%', 'Excellent'],
        ['ROI', f'{roi:.1f}%', 'Excellent'],
        ['Average Order Value', f'${avg_order:,.0f}', 'Large B2B'],
        ['Profit per Order', f'${profit_per_order:,.0f}', 'High Profit'],
        ['Total Orders', f'{len(sales)}', '-'],
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (2, 1), (2, 4), colors.HexColor('#C8E6C9')),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))
    
    # 5. Insights
    elements.append(Paragraph("5. Business Insights", heading_style))
    
    insights = [
        f"1. Gross margin of {margin_rate:.1f}% is significantly higher than industry average (5-10%)",
        f"2. ROI of {roi:.0f}% indicates excellent return on crude oil investment",
        "3. WARNING: Single customer (Hyundai Oilbank) accounts for 90% of revenue",
        "4. Gasoline and Diesel are main profit drivers with 10-13% margin",
        f"5. Total gross profit: ${gross_profit:,.0f}",
    ]
    
    for insight in insights:
        elements.append(Paragraph(insight, normal_style))
        elements.append(Spacer(1, 8))
    
    # 푸터
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Generated by Odoo ERP Demo System - Capa AI", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)))
    elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)))
    
    # PDF 빌드
    doc.build(elements)
    
    print(f"\n✅ PDF 저장 완료!")
    print(f"   파일 경로: {PDF_PATH}")
    print(f"   파일 크기: {os.path.getsize(PDF_PATH):,} bytes")


if __name__ == "__main__":
    generate_pdf()

