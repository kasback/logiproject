from odoo import models, fields, api


class Os(models.Model):
    _name = "men_projet.os"
    _rec_name = "nom"

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Intitulé')
    responsable = fields.Many2one('res.partner')
    programme_id = fields.Many2one('men_projet.programme')
    osg_id = fields.Many2one('men_projet.os_global', default=lambda self: self._get_osg(), string="Objectif global")
    op_ids = fields.One2many('men_projet.op', 'os_id', string="Objectifs Projets")
    risques = fields.One2many('men_projet.risque', 'os_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'os_id')
    indicateur_efficacite = fields.Float('Indicateur d\'éfficacité')
    description = fields.Text()

    @api.model
    def _get_osg(self):
        osg_id = self._context.get('osg_id')
        return osg_id

    @api.model
    def create(self, vals):
        res = super(Os, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.os') or '/'
        res['sequence'] = seq
        return res
