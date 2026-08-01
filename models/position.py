from odoo import models, fields, api


class InventoryPosition(models.Model):
    _name = 'inventory.position'
    _description = 'Imported Position'
    _order = 'create_date desc, id desc'

    external_id = fields.Char(string='External ID', required=True)
    title = fields.Char(string='Position Title', required=True)
    attribute_ids = fields.One2many('inventory.position.attribute', 'position_id', string='Attributes')
    attribute_count = fields.Integer(
        string='Attribute Count',
        compute='_compute_attribute_count',
        store=True,
    )

    @api.depends('attribute_ids')
    def _compute_attribute_count(self):
        for position in self:
            position.attribute_count = len(position.attribute_ids)


class PositionAttribute(models.Model):
    _name = 'inventory.position.attribute'
    _description = 'Position Attribute Stats'
    _order = 'attr_type, title'

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

    # Shared
    stat_count = fields.Integer(string='Record Count')

    # Numeric
    stat_min = fields.Float(string='Min')
    stat_max = fields.Float(string='Max')
    stat_avg = fields.Float(string='Average')

    # Choice / Text
    stat_top_values = fields.Char(string='Top Values')
    stat_distribution = fields.Json(string='Distribution')
    stat_unique_count = fields.Integer(string='Unique Count')

    # Boolean
    stat_true_count = fields.Integer(string='True Count')
    stat_false_count = fields.Integer(string='False Count')
    stat_true_percentage = fields.Float(string='True Percentage')

    # Date
    stat_earliest = fields.Date(string='Earliest')
    stat_latest = fields.Date(string='Latest')

    # Date Period
    stat_earliest_start = fields.Date(string='Earliest Start')
    stat_latest_end = fields.Date(string='Latest End')
    stat_avg_duration_days = fields.Float(string='Avg Duration (days)')

    # Markdown
    stat_total_entries = fields.Integer(string='Total Entries')
    stat_avg_word_count = fields.Float(string='Avg Word Count')
