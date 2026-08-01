import requests
from odoo import models, fields, _
from odoo.exceptions import UserError


class PositionImportWizard(models.TransientModel):
    _name = 'position.import.wizard'
    _description = 'Import Positions via API Token'

    api_endpoint = fields.Char(
        string='API Endpoint',
        default='http://localhost:5000/integration/aggregate-position/cms4h2ldb0001e4v2jj7x4b75',
        required=True
    )
    api_token = fields.Char(string='API Token', required=True)

    def action_import_positions(self):
        if not self.api_token:
            raise UserError(_("Please enter an API Token!"))

        headers = {'x-api-key': self.api_token}

        try:
            response = requests.get(self.api_endpoint, headers=headers, timeout=10)
            if response.status_code != 200:
                raise UserError(_("Server returned error code %s") % response.status_code)
            data = response.json()
        except Exception as e:
            raise UserError(_("Failed to reach API: %s") % str(e))

        PositionObj = self.env['inventory.position']

        pos_data = data.get("data")

        # Search by external ID for upserting
        pos = PositionObj.search([('external_id', '=', str(pos_data['id']))], limit=1)

        vals = {
            'title': pos_data['title'],
            'external_id': str(pos_data['id']),
        }

        attr_lines = []
        for attr in pos_data.get('attributes', []):
            stats = attr.get('stats', {})
            attr_type = attr.get('type', 'TEXT')
            title = attr['title']

            summary = self._build_summary(attr_type, stats)
            attr_vals = self._build_attribute_vals(attr_type, stats)
            attr_vals.update({
                'title': title,
                'attr_type': attr_type,
                'summary_display': summary,
            })
            attr_lines.append((0, 0, attr_vals))

        vals['attribute_ids'] = [(5, 0, 0)] + attr_lines

        if pos:
            pos.write(vals)
        else:
            PositionObj.create(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _build_attribute_vals(self, attr_type, stats):
        vals = {'stat_count': stats.get('count', 0)}

        if attr_type == 'NUMERIC':
            vals.update({
                'stat_min': stats.get('min', 0),
                'stat_max': stats.get('max', 0),
                'stat_avg': stats.get('avg', 0),
            })
        elif attr_type == 'BOOLEAN':
            vals.update({
                'stat_true_count': stats.get('true_count', 0),
                'stat_false_count': stats.get('false_count', 0),
                'stat_true_percentage': stats.get('true_percentage', 0),
            })
        elif attr_type == 'DATE':
            vals.update({
                'stat_earliest': fields.Date.to_date(stats.get('earliest')),
                'stat_latest': fields.Date.to_date(stats.get('latest')),
            })
        elif attr_type == 'DATEPERIOD':
            vals.update({
                'stat_earliest_start': fields.Date.to_date(stats.get('earliest_start')),
                'stat_latest_end': fields.Date.to_date(stats.get('latest_end')),
                'stat_avg_duration_days': stats.get('avg_duration_days', 0),
            })
        elif attr_type == 'CHOICE':
            top = stats.get('top_values', [])
            vals.update({
                'stat_top_values': ', '.join(top) if top else False,
                'stat_distribution': stats.get('distribution') or None,
            })
        elif attr_type == 'TEXT':
            top = stats.get('top_values', [])
            vals.update({
                'stat_top_values': ', '.join(top) if top else False,
                'stat_unique_count': stats.get('unique_count', 0),
            })
        elif attr_type == 'MARKDOWN':
            vals.update({
                'stat_total_entries': stats.get('total_entries', 0),
                'stat_avg_word_count': stats.get('avg_word_count', 0),
            })

        return vals

    def _build_summary(self, attr_type, stats):
        if attr_type == 'NUMERIC':
            return f"Avg: {stats.get('avg', 0)} (Min: {stats.get('min', 0)}, Max: {stats.get('max', 0)})"
        elif attr_type == 'BOOLEAN':
            return f"Yes: {stats.get('true_percentage', 0)}% ({stats.get('true_count', 0)} of {stats.get('count', 0)})"
        elif attr_type == 'DATE':
            return f"Range: {stats.get('earliest', 'N/A')} to {stats.get('latest', 'N/A')}"
        elif attr_type == 'DATEPERIOD':
            return f"Avg Duration: {stats.get('avg_duration_days', 0)} days"
        elif attr_type == 'CHOICE':
            dist = stats.get('distribution') or {}
            if dist:
                return f"{len(dist)} values: {', '.join(stats.get('top_values', [])[:3])}"
            top = stats.get('top_values', [])
            return f"Top: {', '.join(top)}" if top else "No values"
        elif attr_type == 'TEXT':
            top = stats.get('top_values', [])
            return f"Top: {', '.join(top)}" if top else "No values"
        elif attr_type == 'MARKDOWN':
            return f"Entries: {stats.get('total_entries', 0)} (Avg {stats.get('avg_word_count', 0)} words)"
        return f"Records: {stats.get('count', 0)}"
