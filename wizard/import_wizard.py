import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class PositionImportWizard(models.TransientModel):
    _name = 'position.import.wizard'
    _description = 'Import Positions via API Token'

    api_endpoint = fields.Char(
        string='API Endpoint',
        default='http://host.docker.internal:3000/api/public/positions/aggregated',
        required=True
    )
    api_token = fields.Char(string='API Token', required=True)

    def action_import_positions(self):
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(self.api_endpoint, headers=headers, timeout=10)
            if response.status_code != 200:
                raise UserError(_("Server returned error code %s") % response.status_code)
            data = response.json()
        except Exception as e:
            raise UserError(_("Failed to reach API: %s") % str(e))

        PositionObj = self.env['inventory.position']

        for pos_data in data.get('positions', []):
            # Search by external ID for upserting
            pos = PositionObj.search([('external_id', '=', str(pos_data['id']))], limit=1)

            vals = {
                'title': pos_data['title'],
                'external_id': str(pos_data['id']),
                'attribute_ids': [(5, 0, 0)]  # Clear old attribute list
            }

            attr_lines = []
            for attr in pos_data.get('attributes', []):
                stats = attr.get('stats', {})
                attr_type = attr.get('type', 'TEXT')

                # Build summary string based on attribute type
                if attr_type == 'NUMERIC':
                    summary = f"Avg: {stats.get('avg', 0)} (Min: {stats.get('min', 0)}, Max: {stats.get('max', 0)})"
                elif attr_type in ['TEXT', 'CHOICE']:
                    top = stats.get('top_values', [])
                    summary = f"Top: {', '.join(top)}" if top else "No values"
                elif attr_type == 'BOOLEAN':
                    summary = f"Yes: {stats.get('true_percentage', 0)}% ({stats.get('true_count', 0)} total)"
                elif attr_type == 'DATE':
                    summary = f"Range: {stats.get('earliest', 'N/A')} to {stats.get('latest', 'N/A')}"
                elif attr_type == 'DATEPERIOD':
                    summary = f"Avg Duration: {stats.get('avg_duration_days', 0)} days"
                else:
                    summary = f"Records: {stats.get('total_entries', stats.get('count', 0))}"

                attr_lines.append((0, 0, {
                    'title': attr['title'],
                    'attr_type': attr_type,
                    'summary_display': summary,
                }))

            vals['attribute_ids'] = attr_lines

            if pos:
                pos.write(vals)
            else:
                PositionObj.create(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }