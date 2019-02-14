from odoo import fields, models, api


class Oi(models.Model):
    _name = "men_projet.oi"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    code = fields.Char('Code')
    nom = fields.Char('Intitulé')
    description = fields.Text('Description')
    responsable = fields.Many2one('res.partner')
    op_id = fields.Many2one('men_projet.op', default=lambda self: self.env['men_projet.op'].search([('id', '=', self._context.get('op_id'))]))

    risques = fields.One2many('men_projet.risque', 'oi_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'oi_id')
    indicateur_efficacite = fields.Float('Taux d\'éfficacité')
    oos = fields.One2many('men_projet.oo', 'oi_id')
