from odoo import models, fields

class InventoryPosition(models.Model):
    _name = 'inventory.position'
    _description = 'Imported Position'

    external_id = fields.Char(string='External ID', required=True)
    title = fields.Char(string='Position Title', required=True)
    attribute_ids = fields.One2many('inventory.position.attribute', 'position_id', string='Attributes')

class PositionAttribute(models.Model):
    _name = 'inventory.position.attribute'
    _description = 'Position Attribute Stats'

    position_id = fields.Many2one('inventory.position', string='Position', ondelete='cascade')
    title = fields.Char(string='Attribute Title', required=True)
    attr_type = fields.Selection([
        ('NUMERIC', 'Numeric'),
        ('TEXT', 'Text'),
        ('MARKDOWN', 'Markdown'),
        ('IMAGE', 'Image'),
        ('DATE', 'Date'),
        ('DATEPERIOD', 'Date Period'),
        ('BOOLEAN', 'Boolean'),
        ('CHOICE', 'Choice')
    ], string='Type', required=True)

    summary_display = fields.Char(string='Summary / Aggregated Value')