# -*- coding: utf-8 -*-

from odoo import fields, models,api,_
from datetime import timedelta,date
from dateutil.relativedelta import relativedelta
import pdb


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_percentage = fields.Float()
    sale_price_after_discount = fields.Float(compute='_compute_discount_amount',copy=False)
    

    # It computed the price if the discount percentage greater than 0 or else remains the original list price
    @api.depends('discount_percentage')
    def _compute_discount_amount(self):
        for product in self:
            if product.discount_percentage > 0:
                product.sale_price_after_discount = product.list_price - ((product.discount_percentage/100)*product.list_price)
            else:
                product.sale_price_after_discount = product.list_price
    
    # It shows the discounted sale price in along with the strikethrough original sale price value in the foem view in Website Shop  Cartwindow 
    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        combination_info = super()._get_additionnal_combination_info(product_or_template, quantity, date, website)
        # Inherited due to add sale price discount in combination info
        if self.discount_percentage > 0:
            discount_price = self.sale_price_after_discount
            has_discounted_price = True
        else:
            discount_price = self.list_price
            has_discounted_price = False
        combination_info.update({'price': self.sale_price_after_discount,'list_price':self.list_price,'has_discounted_price':has_discounted_price})
        return combination_info
    
    # It shows the discounted sale price in along with the strikethrough original sale price value in the kanban view in Website Shop window 
    def _get_sales_prices(self, pricelist, fiscal_position):
        res = {}
        for template in self:
            if template.discount_percentage > 0:
                template_price_vals = {
                    'price_reduce': template.sale_price_after_discount,
                }
                # if base_price:
                template_price_vals['base_price'] = template.list_price
                res[template.id] = template_price_vals
            else:
                template_price_vals = {
                    'price_reduce': template.list_price,
                }
                # if base_price:
                template_price_vals['base_price'] = template.list_price
                res[template.id] = template_price_vals
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    # It re-computes the price unit in the sale order line base on discount percentage
    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        self = self.with_company(company)
        if price_type == 'standard_price':
            self = self.sudo()
        prices = dict.fromkeys(self.ids, 0.0)
        for template in self:
            if template.discount_percentage > 0:
                price = template.sale_price_after_discount or 0.0
            else:
                price = template[price_type] or 0.0
            price_currency = template.currency_id
            if price_type == 'standard_price':
                if not price and template.product_variant_ids:
                    price = template.product_variant_ids[0].standard_price
                price_currency = template.cost_currency_id
            elif price_type == 'list_price':
                price += template._get_attributes_extra_price()
            if uom:
                price = template.uom_id._compute_price(price, uom)
            if currency:
                price = price_currency._convert(price, currency, company, date)
            prices[template.id] = price
        return prices

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # It sends the discounted unit price to the sale order line when proceed checkouu
    def _prepare_order_line_values(self, product_id, quantity, event_ticket_id=False, **kwargs):
        values = super()._prepare_order_line_values(product_id, quantity, **kwargs)
        if product_id:
            template = self.env['product.product'].browse(product_id).product_tmpl_id
            if template.discount_percentage > 0:
                values['price_unit'] = template.sale_price_after_discount
            else:
                values['price_unit'] = template.list_price
        return values
    