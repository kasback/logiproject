from odoo import fields, models, api


class Oo(models.Model):
    _name = "men_projet.oo"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    code = fields.Char('Code')
    nom = fields.Char('Intitulé')
    description = fields.Text('Description')
    responsable = fields.Many2one('res.partner')
    op_id = fields.Many2one('men_projet.op', default=lambda self: self.env['men_projet.op'].search([('id', '=', self._context.get('op_id'))]), string="Objectif Projet")
    oi_id = fields.Many2one('men_projet.oi', domain=lambda self: [('op_id', '=', self._context.get('op_id'))], string="Livrable", required="True")
    soos = fields.One2many('men_projet.soo', 'oo_id', string="Tâches")
    risques = fields.One2many('men_projet.risque', 'oo_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'oo_id')
    indicateur_efficacite = fields.Float('Taux d\'éfficacité')

    @api.model
    def create(self, vals):
        res = super(Oo, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.oo') or '/'
        res['sequence'] = seq
        return res
