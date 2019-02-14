from odoo import fields, models, api


class Soo(models.Model):
    _name = "men_projet.soo"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    code = fields.Char('Code')
    nom = fields.Char('Intitulé')
    description = fields.Text('Description')
    responsable = fields.Many2one('res.partner')
    op_id = fields.Many2one('men_projet.op', default=lambda self: self.env['men_projet.op'].search([('id', '=', self._context.get('op_id'))]))
    oo_id = fields.Many2one('men_projet.oo', domain=lambda self: [('op_id', '=', self._context.get('op_id'))], string="Livrable", required="True")

    risques = fields.One2many('men_projet.risque', 'soo_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'soo_id')
    indicateur_efficacite = fields.Float('Taux d\'éfficacité')
